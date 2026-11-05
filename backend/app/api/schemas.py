"""Pydantic schemas for PlayRef REST and Streaming APIs."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(description="User question or situation description")
    conversation_id: str | None = Field(default=None, description="Existing conversation UUID")
    stream: bool = Field(default=True, description="Enable SSE streaming deltas")
    language: str | None = Field(
        default=None, description="Override detected language (en, fr, ar)"
    )
    debug: bool = Field(default=False, description="Include timing and candidate scores")


class FeedbackRequest(BaseModel):
    message_id: str = Field(description="UUID of the assistant message")
    rating: int = Field(description="+1 (thumbs up) or -1 (thumbs down)")
    reason: str | None = Field(default=None, description="e.g. wrong_law_cited, incorrect_sanction")
    comment: str | None = Field(default=None, description="Optional user commentary")


class FeedbackResponse(BaseModel):
    id: str
    message_id: str
    rating: int
    status: str = "received"


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    answer_json: dict | None = None
    retrieved_chunk_ids: list[str] | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    created_at: datetime
    language: str
    title: str | None
    messages: list[MessageResponse] = []


class LawSummary(BaseModel):
    law_number: int
    title: str
    chunk_count: int


class LawDetail(BaseModel):
    law_number: int
    title: str
    edition: str
    sections: list[dict]


class HealthResponse(BaseModel):
    status: str
    edition: str
    models: dict[str, str]
    qdrant: str
