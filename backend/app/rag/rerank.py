"""RAG reranking service using cross-encoder with fallback."""

from backend.app.config import settings
from backend.app.llm.rerank import rerank_client
from backend.app.logger import logger
from backend.app.rag.retrieve import ScoredChunk


class RerankerService:
    """Reranks retrieved candidate chunks to top-K using cross-encoder."""

    def __init__(self, top_k: int = settings.rerank_top_k):
        self.top_k = top_k

    async def rerank(
        self,
        query: str,
        candidates: list[ScoredChunk],
        top_k: int = settings.rerank_top_k,
    ) -> list[ScoredChunk]:
        """Rerank candidates using cross-encoder model. Falls back to original order on failure."""
        if not candidates:
            return []

        # Prepare documents text with section hierarchy
        documents = [c.chunk.text_for_embedding for c in candidates]

        try:
            results = await rerank_client.rerank(query=query, documents=documents, top_n=top_k)
            reranked: list[ScoredChunk] = []
            for r in results:
                original_chunk = candidates[r.index].chunk
                reranked.append(
                    ScoredChunk(
                        chunk=original_chunk,
                        score=round(r.score, 4),
                        retrieval_method="cross_encoder",
                    )
                )
            logger.info(
                f"Successfully reranked to top {len(reranked)} chunks",
                extra={"stage": "rerank"},
            )
            return reranked

        except Exception as exc:
            logger.warning(
                f"Reranking failed ({exc}), falling back to top {top_k} retrieval order",
                extra={"stage": "rerank_fallback"},
            )
            return candidates[:top_k]


reranker_service = RerankerService()
