"""Qdrant indexing pipeline for PlayRef with rate-limit protection."""

import asyncio
import uuid

import httpx
from qdrant_client import QdrantClient, models

from backend.app.config import settings
from backend.app.ingestion.models import LawChunk
from backend.app.llm.embeddings import embedding_client, sparse_encoder
from backend.app.logger import logger

_qdrant_singleton: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Connect to remote Qdrant if reachable, else fall back to shared local embedded storage."""
    global _qdrant_singleton
    if _qdrant_singleton is not None:
        return _qdrant_singleton

    if settings.qdrant_url:
        try:
            with httpx.Client(timeout=1.5) as http:
                r = http.get(f"{settings.qdrant_url.rstrip('/')}/readyz")
                if r.status_code == 200:
                    logger.info(f"Connected to remote Qdrant at {settings.qdrant_url}")
                    _qdrant_singleton = QdrantClient(url=settings.qdrant_url)
                    return _qdrant_singleton
        except Exception:
            logger.warning(
                f"Remote Qdrant at {settings.qdrant_url} unreachable. Using local embedded storage at {settings.qdrant_path}"
            )

    _qdrant_singleton = QdrantClient(path=settings.qdrant_path or "data/qdrant_storage")
    return _qdrant_singleton


def init_collection(
    client: QdrantClient,
    collection_name: str = settings.qdrant_collection,
    recreate: bool = False,
) -> None:
    """Ensure the Qdrant collection exists with dense and sparse vector configurations."""
    exists = client.collection_exists(collection_name)
    if exists and recreate:
        logger.info(f"Recreating collection '{collection_name}'")
        client.delete_collection(collection_name)
        exists = False

    if not exists:
        logger.info(f"Creating collection '{collection_name}' with dense (1024) + sparse vectors")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=settings.embedding_dim,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(),
            },
        )


async def index_chunks(
    chunks: list[LawChunk],
    batch_size: int = 64,
    collection_name: str = settings.qdrant_collection,
    recreate: bool = False,
    pause_between_batches: float = 0.0,
) -> int:
    """Embed chunks and upsert into Qdrant idempotently."""
    client = get_qdrant_client()
    init_collection(client, collection_name=collection_name, recreate=recreate)

    total = len(chunks)
    logger.info(
        f"Indexing {total} chunks in batches of {batch_size} (pacing: {pause_between_batches}s)..."
    )

    indexed_count = 0
    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.text_for_embedding for c in batch]

        # Generate dense embeddings via model API
        dense_vecs = await embedding_client.embed_dense(texts)

        # Build Qdrant PointStruct list
        points: list[models.PointStruct] = []
        for chunk, dense_vec in zip(batch, dense_vecs):
            indices, values = sparse_encoder.encode(chunk.text_for_embedding)
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = chunk.model_dump()

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector={
                        "dense": dense_vec,
                        "sparse": models.SparseVector(indices=indices, values=values),
                    },
                    payload=payload,
                )
            )

        client.upsert(collection_name=collection_name, points=points)
        indexed_count += len(points)
        logger.info(f"Indexed batch {indexed_count}/{total} chunks")

        # Polite delay to avoid WAF rate-limit triggers on esprit.tn
        if indexed_count < total:
            await asyncio.sleep(pause_between_batches)

    return indexed_count
