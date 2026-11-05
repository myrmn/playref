"""RAG pipeline module for PlayRef."""

from backend.app.rag.citations import ApplicableLaw, CitationValidator, PlayRefAnswer
from backend.app.rag.generate import GroundedGenerator, generator
from backend.app.rag.parents import ParentExpander, parent_expander
from backend.app.rag.rerank import RerankerService, reranker_service
from backend.app.rag.retrieve import HybridRetriever, ScoredChunk, retriever

__all__ = [
    "retriever",
    "HybridRetriever",
    "ScoredChunk",
    "reranker_service",
    "RerankerService",
    "generator",
    "GroundedGenerator",
    "CitationValidator",
    "PlayRefAnswer",
    "ApplicableLaw",
    "parent_expander",
    "ParentExpander",
]
