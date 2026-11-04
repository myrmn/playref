"""Configuration module for PlayRef using Pydantic Settings."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env is loaded into environment
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Provider settings
    llm_base_url: str = Field(
        default_factory=lambda: (
            os.getenv("LLM_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://aiforge.esprit.tn/api/v1"
        )
    )
    llm_api_key: str = Field(
        default_factory=lambda: os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    )
    llm_provider: str = Field(default="openai")

    # Model names
    model_chat: str = Field(
        default_factory=lambda: os.getenv("MODEL_CHAT") or os.getenv("LLM_MODEL_MAIN") or "Qwen3.6-35B-A3B"
    )
    model_fast: str = Field(
        default_factory=lambda: os.getenv("MODEL_ROUTER") or os.getenv("LLM_MODEL_FAST") or "Llama-3.2-3B"
    )
    model_reasoning: str = Field(
        default_factory=lambda: (
            os.getenv("MODEL_REASONING") or os.getenv("LLM_FALLBACK_MODEL") or "Qwen3.6-27B"
        )
    )
    model_router: str = Field(
        default_factory=lambda: os.getenv("MODEL_ROUTER") or os.getenv("LLM_MODEL_FAST") or "Llama-3.2-3B"
    )
    model_vision: str = Field(default="Gemma-3-4B-IT")
    model_ocr: str = Field(default="Unlimited-OCR")
    model_embedding: str = Field(
        default_factory=lambda: os.getenv("MODEL_EMBEDDING") or os.getenv("EMBEDDING_MODEL") or "BGE-M3-Embeddings"
    )
    model_rerank: str = Field(default="BGE-Reranker-v2-m3")

    # Embeddings
    embedding_dim: int = Field(default=1024)

    # Qdrant & Storage
    qdrant_url: Optional[str] = Field(default="http://localhost:6333")
    qdrant_path: Optional[str] = Field(default="data/qdrant_storage")
    qdrant_collection: str = Field(default="playref_laws")

    # Database & Redis
    database_url: str = Field(
        default="postgresql+asyncpg://playref:playref@localhost:5432/playref"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")

    # App Parameters
    laws_edition: str = Field(default="2026/27")
    retrieve_top_k: int = Field(default=30)
    rerank_top_k: int = Field(default=6)
    max_upload_mb: int = Field(default=20)
    max_video_seconds: int = Field(default=15)
    run_integration: int = Field(default=0)


settings = Settings()
