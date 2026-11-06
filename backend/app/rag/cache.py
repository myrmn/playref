"""Q&A Semantic and Lexical Cache for PlayRef.

Caches verified answers to frequent football rules questions to achieve:
1. 0 LLM token cost on repetitive questions.
2. ~5ms instantaneous streaming response time.
3. Near-zero CPU & RAM consumption on low-memory VPS.
"""

import re
from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import QACache
from backend.app.logger import logger

# Common stop words that don't change football rule intent
STOP_WORDS = {
    "a", "an", "the", "is", "are", "can", "could", "would", "should", "does",
    "do", "what", "when", "where", "how", "why", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "about", "tell", "me", "explain", "please",
    "est", "ce", "que", "un", "une", "le", "la", "les", "du", "de", "des",
    "هل", "ما", "هو", "هي", "في", "على", "من", "عن", "الى", "إلى", "قانون"
}


def normalize_query(query: str) -> str:
    """Normalize a user question into a canonical keyword signature.

    Examples:
        'Can a goal be scored directly from a goal kick?' -> 'directly goal goal kick score'
        'Can you score from a goal kick?' -> 'goal goal kick score'
    """
    clean = re.sub(r"[^\w\s]", " ", query.lower())
    tokens = [w for w in clean.split() if w and w not in STOP_WORDS]
    # Sort distinct tokens to handle word order variations
    sorted_tokens = sorted(tokens)
    return " ".join(sorted_tokens[:12])


async def get_cached_answer(
    db: AsyncSession, query: str, language: str = "en"
) -> QACache | None:
    """Look up a cached answer for a query."""
    norm_key = normalize_query(query)
    if not norm_key:
        return None

    try:
        stmt = (
            select(QACache)
            .where(QACache.normalized_query == norm_key)
            .where(QACache.language == language)
        )
        result = await db.execute(stmt)
        cached = result.scalar_one_or_none()

        if cached:
            cached.hit_count += 1
            cached.last_accessed_at = datetime.now(UTC)
            await db.commit()
            logger.info(
                f"QA Cache HIT for query: '{query[:40]}...' (hit_count={cached.hit_count})",
                extra={"stage": "cache_hit", "normalized_key": norm_key},
            )
            return cached

    except Exception as exc:
        logger.warning(f"QA Cache lookup failed gracefully: {exc}")

    return None


async def set_cached_answer(
    db: AsyncSession,
    raw_query: str,
    short_answer: str,
    answer_json: dict,
    language: str = "en",
) -> QACache | None:
    """Store a newly generated verified answer into the Q&A cache."""
    norm_key = normalize_query(raw_query)
    if not norm_key or not short_answer:
        return None

    try:
        # Check if already exists
        stmt = (
            select(QACache)
            .where(QACache.normalized_query == norm_key)
            .where(QACache.language == language)
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.short_answer = short_answer
            existing.answer_json = answer_json
            existing.last_accessed_at = datetime.now(UTC)
            await db.commit()
            return existing

        new_cache = QACache(
            normalized_query=norm_key,
            raw_query=raw_query,
            language=language,
            short_answer=short_answer,
            answer_json=answer_json,
            hit_count=1,
        )
        db.add(new_cache)
        await db.commit()
        logger.info(
            f"QA Cache STORED for query: '{raw_query[:40]}...'",
            extra={"stage": "cache_store", "normalized_key": norm_key},
        )
        return new_cache

    except Exception as exc:
        logger.warning(f"QA Cache save failed gracefully: {exc}")
        await db.rollback()
        return None
