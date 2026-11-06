"""FastAPI route definitions for PlayRef API."""

import json
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from qdrant_client import models
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.api.schemas import (
    ChatRequest,
    ConversationResponse,
    ConversationSummary,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    LawDetail,
    LawSummary,
    MessageResponse,
)
from backend.app.config import settings
from backend.app.db.models import Conversation, Feedback, Message
from backend.app.db.rate_limiter import rate_limiter
from backend.app.db.session import get_db
from backend.app.ingestion.indexer import get_qdrant_client
from backend.app.logger import logger
from backend.app.metrics import count_tokens, metrics_collector
from backend.app.rag.cache import get_cached_answer, set_cached_answer
from backend.app.rag.generate import generator
from backend.app.rag.rerank import reranker_service
from backend.app.rag.retrieve import retriever
from backend.app.rag.rewrite import rewriter
from backend.app.rag.router import router

api_router = APIRouter()


def verify_admin_key(request: Request, admin_key: str | None = None) -> None:
    """Validate admin key from header or query param."""
    header_key = request.headers.get("X-Admin-Key")
    query_key = admin_key or request.query_params.get("admin_key")
    provided = header_key or query_key
    if not provided or provided != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid or missing admin key")


@api_router.get("/admin/stats")
async def get_admin_stats(request: Request, admin_key: str | None = None):
    """Retrieve operational metrics, stage latencies, memory, and cache hit rates."""
    verify_admin_key(request, admin_key)
    return metrics_collector.get_stats()


@api_router.get("/metrics")
async def get_metrics(request: Request, admin_key: str | None = None):
    """Alias for /admin/stats to support external scrapers."""
    verify_admin_key(request, admin_key)
    return metrics_collector.get_stats()


@api_router.post("/admin/stats/reset")
async def reset_admin_stats(request: Request, admin_key: str | None = None):
    """Reset accumulated metrics for clean benchmarking runs."""
    verify_admin_key(request, admin_key)
    metrics_collector.reset()
    return {"status": "reset", "timestamp": time.time()}


@api_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    q_client = get_qdrant_client()
    q_status = "connected"
    try:
        q_client.count(settings.qdrant_collection).count
    except Exception as exc:
        q_status = f"degraded: {exc}"

    return HealthResponse(
        status="healthy",
        edition=settings.laws_edition,
        models={
            "chat": settings.model_chat,
            "router": settings.model_router,
            "embedding": settings.model_embedding,
            "rerank": settings.model_rerank,
        },
        qdrant=q_status,
    )


@api_router.post("/chat")
async def chat_endpoint(
    req: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Chat endpoint supporting SSE streaming and non-streaming."""
    # 1. Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait a minute.")

    # 2. Conversation resolution
    conv_id = req.conversation_id or str(uuid.uuid4())
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conv_id)
        .options(selectinload(Conversation.messages))
    )
    conv = conv_result.scalar_one_or_none()
    history = []
    if not conv:
        conv = Conversation(id=conv_id, language=req.language or "en", title=req.query[:60])
        db.add(conv)
        await db.commit()
    else:
        for m in conv.messages[-6:]:
            history.append({"role": m.role, "content": m.content})

    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    async def sse_event_stream():
        start_total = time.perf_counter()

        # Step 0: Fast Q&A Cache lookup (avoids 100% of LLM tokens if already answered)
        target_lang = req.language or "en"
        if not history:
            cached = await get_cached_answer(db, req.query, target_lang)
            if cached:
                bot_msg_id = str(uuid.uuid4())
                total_ms = round((time.perf_counter() - start_total) * 1000, 1)
                prompt_toks = count_tokens(req.query)
                comp_toks = count_tokens(cached.short_answer)

                metrics_collector.record_request(
                    request_id=req_id,
                    stage_timings={"total": total_ms, "ttft": total_ms},
                    cache_hit="exact",
                    prompt_tokens=prompt_toks,
                    completion_tokens=comp_toks,
                    status_code=200,
                )
                logger.info(
                    "Chat request completed (cache hit)",
                    extra={
                        "request_id": req_id,
                        "stage": "chat_cache_hit",
                        "duration_ms": total_ms,
                        "ttft_ms": total_ms,
                        "cache_hit": "exact",
                        "tokens": {
                            "prompt": prompt_toks,
                            "completion": comp_toks,
                            "total": prompt_toks + comp_toks,
                        },
                        "rss_mb": metrics_collector.get_process_rss_mb(),
                    },
                )
                yield f"event: route\ndata: {json.dumps({'intent': 'rules_question', 'lang': target_lang, 'duration_ms': 1.0, 'cached': True})}\n\n"
                yield f"event: delta\ndata: {json.dumps({'content': cached.short_answer})}\n\n"
                yield f"event: answer\ndata: {json.dumps(cached.answer_json)}\n\n"
                yield f"event: done\ndata: {json.dumps({'timings': {'total_ms': total_ms, 'cached': True}, 'conversation_id': conv_id, 'message_id': bot_msg_id})}\n\n"

                msg_user = Message(conversation_id=conv_id, role="user", content=req.query)
                msg_bot = Message(
                    id=bot_msg_id,
                    conversation_id=conv_id,
                    role="assistant",
                    content=cached.short_answer,
                    answer_json=cached.answer_json,
                    retrieved_chunk_ids=[],
                )
                db.add_all([msg_user, msg_bot])
                await db.commit()
                return

        # Step A: Routing
        t0 = time.perf_counter()
        route_res = await router.route(req.query)
        route_ms = round((time.perf_counter() - t0) * 1000, 1)

        target_lang = req.language or route_res.lang
        yield f"event: route\ndata: {json.dumps({'intent': route_res.intent, 'lang': target_lang, 'duration_ms': route_ms})}\n\n"

        # Off-topic immediate redirect
        if route_res.is_off_topic:
            redirect_text = (
                route_res.redirect_message
                or "Please ask a question about football Laws of the Game."
            )
            yield f"event: delta\ndata: {json.dumps({'content': redirect_text})}\n\n"
            final_obj = {
                "short_answer": redirect_text,
                "applicable_laws": [],
                "interpretations": [],
                "what_would_change_the_decision": [],
                "assumptions": [],
                "needs_more_info": False,
                "clarifying_question": None,
                "language": target_lang,
            }
            bot_msg_id = str(uuid.uuid4())
            total_ms = round((time.perf_counter() - start_total) * 1000, 1)
            prompt_toks = count_tokens(req.query)
            comp_toks = count_tokens(redirect_text)

            metrics_collector.record_request(
                request_id=req_id,
                stage_timings={"router": route_ms, "total": total_ms, "ttft": total_ms},
                cache_hit="miss",
                prompt_tokens=prompt_toks,
                completion_tokens=comp_toks,
                status_code=200,
            )
            yield f"event: answer\ndata: {json.dumps(final_obj)}\n\n"
            yield f"event: done\ndata: {json.dumps({'total_ms': total_ms, 'conversation_id': conv_id, 'message_id': bot_msg_id})}\n\n"

            # Save messages
            msg_user = Message(conversation_id=conv_id, role="user", content=req.query)
            msg_bot = Message(
                id=bot_msg_id,
                conversation_id=conv_id,
                role="assistant",
                content=redirect_text,
                answer_json=final_obj,
                retrieved_chunk_ids=[],
            )
            db.add_all([msg_user, msg_bot])
            await db.commit()
            return

        # Step B: Query Rewrite
        t1 = time.perf_counter()
        rewrite_res = await rewriter.rewrite(req.query, history=history)
        rewrite_ms = round((time.perf_counter() - t1) * 1000, 1)

        # Step C: Retrieval
        t2 = time.perf_counter()
        candidates = await retriever.retrieve(
            query=rewrite_res.standalone_query,
            top_k=settings.retrieve_top_k,
            law_number_filter=rewrite_res.law_hint,
        )
        retrieve_ms = round((time.perf_counter() - t2) * 1000, 1)
        embed_ms = getattr(retriever, "last_embed_ms", 0.0)
        pure_retrieve_ms = max(0.0, round(retrieve_ms - embed_ms, 1))

        # Step D: Cross-Encoder Rerank
        t3 = time.perf_counter()
        reranked = await reranker_service.rerank(
            query=rewrite_res.standalone_query,
            candidates=candidates,
            top_k=settings.rerank_top_k,
        )
        rerank_ms = round((time.perf_counter() - t3) * 1000, 1)

        # Step E: Grounded Generation (Streaming short_answer tokens then final answer)
        t_gen_start = time.perf_counter()
        ttft_ms = None
        final_answer_payload = None
        async for gen_event in generator.stream_generate(
            query=req.query,
            scored_chunks=reranked,
            language=target_lang,
        ):
            if gen_event["event"] == "delta":
                if ttft_ms is None:
                    ttft_ms = round((time.perf_counter() - start_total) * 1000, 1)
                yield f"event: delta\ndata: {json.dumps(gen_event['data'])}\n\n"
            elif gen_event["event"] == "answer":
                final_answer_payload = gen_event["data"]
                yield f"event: answer\ndata: {json.dumps(final_answer_payload)}\n\n"

        gen_ms = round((time.perf_counter() - t_gen_start) * 1000, 1)
        if ttft_ms is None:
            ttft_ms = round((time.perf_counter() - start_total) * 1000, 1)

        total_ms = round((time.perf_counter() - start_total) * 1000, 1)
        timings = {
            "route_ms": route_ms,
            "rewrite_ms": rewrite_ms,
            "embed_ms": embed_ms,
            "retrieve_ms": pure_retrieve_ms,
            "rerank_ms": rerank_ms,
            "generate_ms": gen_ms,
            "ttft_ms": ttft_ms,
            "total_ms": total_ms,
        }
        bot_msg_id = str(uuid.uuid4())

        prompt_toks = count_tokens(req.query) + sum(
            count_tokens(sc.chunk.clean_text) for sc in reranked
        )
        comp_toks = (
            count_tokens(json.dumps(final_answer_payload)) if final_answer_payload else 0
        )

        metrics_collector.record_request(
            request_id=req_id,
            stage_timings={
                "router": route_ms,
                "rewrite": rewrite_ms,
                "embed": embed_ms,
                "retrieve": pure_retrieve_ms,
                "rerank": rerank_ms,
                "generate": gen_ms,
                "ttft": ttft_ms,
                "total": total_ms,
            },
            cache_hit="miss",
            prompt_tokens=prompt_toks,
            completion_tokens=comp_toks,
            status_code=200,
        )
        logger.info(
            "Chat SSE completed",
            extra={
                "request_id": req_id,
                "stage": "chat_complete",
                "duration_ms": total_ms,
                "ttft_ms": ttft_ms,
                "timings": timings,
                "tokens": {
                    "prompt": prompt_toks,
                    "completion": comp_toks,
                    "total": prompt_toks + comp_toks,
                },
                "rss_mb": metrics_collector.get_process_rss_mb(),
            },
        )

        yield f"event: done\ndata: {json.dumps({'timings': timings, 'conversation_id': conv_id, 'message_id': bot_msg_id})}\n\n"

        # Persist to database
        if final_answer_payload:
            chunk_ids = [sc.chunk.chunk_id for sc in reranked]
            msg_user = Message(conversation_id=conv_id, role="user", content=req.query)
            msg_bot = Message(
                id=bot_msg_id,
                conversation_id=conv_id,
                role="assistant",
                content=final_answer_payload.get("short_answer", ""),
                answer_json=final_answer_payload,
                retrieved_chunk_ids=chunk_ids,
            )
            db.add_all([msg_user, msg_bot])
            await db.commit()

            # Cache verified response for future users
            if not route_res.is_off_topic and not final_answer_payload.get("needs_more_info"):
                await set_cached_answer(
                    db,
                    raw_query=req.query,
                    short_answer=final_answer_payload.get("short_answer", ""),
                    answer_json=final_answer_payload,
                    language=target_lang,
                )

    if req.stream:
        return StreamingResponse(sse_event_stream(), media_type="text/event-stream")

    # Non-streaming request
    start_total = time.perf_counter()
    target_lang = req.language or "en"
    if not history:
        cached = await get_cached_answer(db, req.query, target_lang)
        if cached:
            bot_msg_id = str(uuid.uuid4())
            total_ms = round((time.perf_counter() - start_total) * 1000, 1)
            prompt_toks = count_tokens(req.query)
            comp_toks = count_tokens(cached.short_answer)

            metrics_collector.record_request(
                request_id=req_id,
                stage_timings={"total": total_ms, "ttft": total_ms},
                cache_hit="exact",
                prompt_tokens=prompt_toks,
                completion_tokens=comp_toks,
                status_code=200,
            )
            msg_user = Message(conversation_id=conv_id, role="user", content=req.query)
            msg_bot = Message(
                id=bot_msg_id,
                conversation_id=conv_id,
                role="assistant",
                content=cached.short_answer,
                answer_json=cached.answer_json,
                retrieved_chunk_ids=[],
            )
            db.add_all([msg_user, msg_bot])
            await db.commit()
            return {
                "conversation_id": conv_id,
                "message_id": bot_msg_id,
                "answer": cached.answer_json,
                "timings": {"total_ms": total_ms, "cached": True},
            }

    t0 = time.perf_counter()
    route_res = await router.route(req.query)
    route_ms = round((time.perf_counter() - t0) * 1000, 1)
    target_lang = req.language or route_res.lang

    if route_res.is_off_topic:
        answer_dict = {
            "short_answer": route_res.redirect_message
            or "Please ask about football Laws of the Game.",
            "applicable_laws": [],
            "interpretations": [],
            "what_would_change_the_decision": [],
            "assumptions": [],
            "needs_more_info": False,
            "clarifying_question": None,
            "language": target_lang,
        }
        reranked = []
        pure_retrieve_ms = 0.0
        rewrite_ms = 0.0
        embed_ms = 0.0
        rerank_ms = 0.0
        gen_ms = 0.0
    else:
        t1 = time.perf_counter()
        rewrite_res = await rewriter.rewrite(req.query, history=history)
        rewrite_ms = round((time.perf_counter() - t1) * 1000, 1)

        t2 = time.perf_counter()
        candidates = await retriever.retrieve(
            query=rewrite_res.standalone_query,
            top_k=settings.retrieve_top_k,
            law_number_filter=rewrite_res.law_hint,
        )
        retrieve_ms = round((time.perf_counter() - t2) * 1000, 1)
        embed_ms = getattr(retriever, "last_embed_ms", 0.0)
        pure_retrieve_ms = max(0.0, round(retrieve_ms - embed_ms, 1))

        t3 = time.perf_counter()
        reranked = await reranker_service.rerank(
            query=rewrite_res.standalone_query,
            candidates=candidates,
            top_k=settings.rerank_top_k,
        )
        rerank_ms = round((time.perf_counter() - t3) * 1000, 1)

        t4 = time.perf_counter()
        answer = await generator.generate(
            query=req.query,
            scored_chunks=reranked,
            language=target_lang,
        )
        gen_ms = round((time.perf_counter() - t4) * 1000, 1)
        answer_dict = answer.model_dump()

    total_ms = round((time.perf_counter() - start_total) * 1000, 1)
    prompt_toks = count_tokens(req.query) + sum(
        count_tokens(sc.chunk.clean_text) for sc in reranked
    )
    comp_toks = count_tokens(json.dumps(answer_dict))

    metrics_collector.record_request(
        request_id=req_id,
        stage_timings={
            "router": route_ms,
            "rewrite": rewrite_ms,
            "embed": embed_ms,
            "retrieve": pure_retrieve_ms,
            "rerank": rerank_ms,
            "generate": gen_ms,
            "ttft": total_ms,
            "total": total_ms,
        },
        cache_hit="miss",
        prompt_tokens=prompt_toks,
        completion_tokens=comp_toks,
        status_code=200,
    )
    logger.info(
        "Chat non-streaming completed",
        extra={
            "request_id": req_id,
            "stage": "chat_complete_non_stream",
            "duration_ms": total_ms,
            "timings": {
                "route_ms": route_ms,
                "rewrite_ms": rewrite_ms,
                "embed_ms": embed_ms,
                "retrieve_ms": pure_retrieve_ms,
                "rerank_ms": rerank_ms,
                "generate_ms": gen_ms,
                "total_ms": total_ms,
            },
            "tokens": {
                "prompt": prompt_toks,
                "completion": comp_toks,
                "total": prompt_toks + comp_toks,
            },
            "rss_mb": metrics_collector.get_process_rss_mb(),
        },
    )

    # Save to db
    bot_msg_id = str(uuid.uuid4())
    msg_user = Message(conversation_id=conv_id, role="user", content=req.query)
    msg_bot = Message(
        id=bot_msg_id,
        conversation_id=conv_id,
        role="assistant",
        content=answer_dict.get("short_answer", ""),
        answer_json=answer_dict,
        retrieved_chunk_ids=[sc.chunk.chunk_id for sc in reranked]
        if not route_res.is_off_topic
        else [],
    )
    db.add_all([msg_user, msg_bot])
    await db.commit()

    if not route_res.is_off_topic and not answer_dict.get("needs_more_info"):
        await set_cached_answer(
            db,
            raw_query=req.query,
            short_answer=answer_dict.get("short_answer", ""),
            answer_json=answer_dict,
            language=target_lang,
        )

    return {"conversation_id": conv_id, "message_id": bot_msg_id, "answer": answer_dict}


@api_router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Fetch recent conversations for the sidebar history."""
    res = await db.execute(
        select(Conversation)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    convs = res.scalars().all()
    return [
        ConversationSummary(
            id=c.id,
            created_at=c.created_at,
            language=c.language,
            title=c.title,
        )
        for c in convs
    ]


@api_router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch complete conversation history with messages and citations."""
    res = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            answer_json=m.answer_json,
            retrieved_chunk_ids=m.retrieved_chunk_ids,
            created_at=m.created_at,
        )
        for m in conv.messages
    ]
    return ConversationResponse(
        id=conv.id,
        created_at=conv.created_at,
        language=conv.language,
        title=conv.title,
        messages=messages,
    )


@api_router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    """Submit user rating and feedback on an answer."""
    msg_res = await db.execute(select(Message).where(Message.id == req.message_id))
    msg = msg_res.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    fb = Feedback(
        message_id=req.message_id,
        rating=req.rating,
        reason=req.reason,
        comment=req.comment,
    )
    db.add(fb)
    await db.commit()
    return FeedbackResponse(id=fb.id, message_id=fb.message_id, rating=fb.rating)


@api_router.get("/laws", response_model=list[LawSummary])
async def list_laws():
    """List all 17 Laws with chunk counts for the Law browser sidebar."""
    q_client = get_qdrant_client()
    law_chunks: dict[int, dict] = {}

    # Scroll through collection
    offset = None
    while True:
        results, next_offset = q_client.scroll(
            collection_name=settings.qdrant_collection,
            limit=100,
            offset=offset,
            with_payload=True,
        )
        for p in results:
            ln = p.payload.get("law_number")
            if ln and 1 <= ln <= 17:
                if ln not in law_chunks:
                    law_chunks[ln] = {
                        "law_number": ln,
                        "title": p.payload.get("law_title"),
                        "count": 0,
                    }
                law_chunks[ln]["count"] += 1

        if next_offset is None:
            break
        offset = next_offset

    sorted_laws = sorted(law_chunks.values(), key=lambda x: x["law_number"])
    return [
        LawSummary(law_number=d["law_number"], title=d["title"], chunk_count=d["count"])
        for d in sorted_laws
    ]


@api_router.get("/laws/{law_number}", response_model=LawDetail)
async def get_law(law_number: int):
    """Get sections and text of a specific Law."""
    q_client = get_qdrant_client()
    results, _ = q_client.scroll(
        collection_name=settings.qdrant_collection,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="law_number", match=models.MatchValue(value=law_number))
            ]
        ),
        limit=100,
        with_payload=True,
    )
    if not results:
        raise HTTPException(status_code=404, detail=f"Law {law_number} not found")

    first = results[0].payload
    sections = [
        {
            "chunk_id": p.payload.get("chunk_id"),
            "section_path": p.payload.get("section_path"),
            "page": p.payload.get("page"),
            "text": p.payload.get("clean_text"),
        }
        for p in results
    ]

    return LawDetail(
        law_number=law_number,
        title=first.get("law_title", f"Law {law_number}"),
        edition=first.get("edition", settings.laws_edition),
        sections=sections,
    )


@api_router.get("/chunks/{chunk_id}")
async def get_chunk(chunk_id: str):
    """Retrieve exact chunk text and metadata for citation drawer."""
    q_client = get_qdrant_client()
    results, _ = q_client.scroll(
        collection_name=settings.qdrant_collection,
        scroll_filter=models.Filter(
            must=[models.FieldCondition(key="chunk_id", match=models.MatchValue(value=chunk_id))]
        ),
        limit=1,
        with_payload=True,
    )
    if not results:
        raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found")

    return results[0].payload
