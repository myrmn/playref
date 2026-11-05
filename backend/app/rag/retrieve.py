"""Hybrid retrieval with Dense + Sparse Reciprocal Rank Fusion (RRF)."""

from pydantic import BaseModel
from qdrant_client import models

from backend.app.config import settings
from backend.app.ingestion.indexer import get_qdrant_client
from backend.app.ingestion.models import LawChunk
from backend.app.llm.embeddings import embedding_client, sparse_encoder
from backend.app.logger import logger


class ScoredChunk(BaseModel):
    chunk: LawChunk
    score: float
    retrieval_method: str = "hybrid"


class HybridRetriever:
    """Performs hybrid dense + sparse retrieval with Reciprocal Rank Fusion."""

    def __init__(self, collection_name: str = settings.qdrant_collection):
        self.collection_name = collection_name
        self.client = get_qdrant_client()

    async def retrieve(
        self,
        query: str,
        top_k: int = 30,
        law_number_filter: int | None = None,
        rrf_k: int = 60,
    ) -> list[ScoredChunk]:
        """Perform hybrid retrieval with dense vector + sparse BM25 fusion."""
        # 1. Build query vectors
        dense_vec = await embedding_client.embed_query(query)
        sparse_indices, sparse_values = sparse_encoder.encode(query)

        # 2. Build optional filter
        query_filter = None
        if law_number_filter is not None:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="law_number",
                        match=models.MatchValue(value=law_number_filter),
                    )
                ]
            )

        # 3. Dense search
        dense_results = self.client.query_points(
            collection_name=self.collection_name,
            query=dense_vec,
            using="dense",
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        ).points

        # 4. Sparse search
        sparse_results = []
        if sparse_indices and any(v > 0 for v in sparse_values):
            sparse_query = models.SparseVector(indices=sparse_indices, values=sparse_values)
            sparse_results = self.client.query_points(
                collection_name=self.collection_name,
                query=sparse_query,
                using="sparse",
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            ).points

        # 5. Reciprocal Rank Fusion (RRF)
        rrf_scores: dict[str, float] = {}
        payload_map: dict[str, dict] = {}

        for rank, p in enumerate(dense_results, 1):
            pid = p.payload["chunk_id"]
            rrf_scores[pid] = rrf_scores.get(pid, 0.0) + (1.0 / (rrf_k + rank))
            payload_map[pid] = p.payload

        for rank, p in enumerate(sparse_results, 1):
            pid = p.payload["chunk_id"]
            rrf_scores[pid] = rrf_scores.get(pid, 0.0) + (1.0 / (rrf_k + rank))
            payload_map[pid] = p.payload

        # Sort descending by RRF score
        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results: list[ScoredChunk] = []
        for pid, score in sorted_items:
            payload = payload_map[pid]
            chunk = LawChunk(**payload)
            results.append(ScoredChunk(chunk=chunk, score=round(score, 5), retrieval_method="rrf"))

        logger.info(
            f"Hybrid retrieval found {len(results)} chunks for query: '{query[:40]}...'",
            extra={"stage": "retrieve"},
        )
        return results


retriever = HybridRetriever()
