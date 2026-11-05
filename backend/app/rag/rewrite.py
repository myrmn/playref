"""History-aware Query Rewriting for PlayRef."""

import json
import re

from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.llm.chat import chat_client
from backend.app.logger import logger


class RewriteResult(BaseModel):
    standalone_query: str = Field(description="Self-contained English query incorporating history")
    keywords: list[str] = Field(default_factory=list, description="Extracted search keywords")
    law_hint: int | None = Field(default=None, description="Optional IFAB Law number (1-17)")


REWRITE_PROMPT = """You are a query rewriting specialist for football (soccer) IFAB Laws of the Game retrieval.

Given the chat history and the latest user message:
1. Translate non-English queries (Arabic, French, Tunisian dialect, etc.) into a standalone English query.
2. Resolve ambiguous follow-ups (e.g., "what if it was outside the penalty box?", "and if it was intentional?") using context from previous turns.
3. Extract 3-6 relevant football rule keywords.
4. If a specific Law clearly applies (Laws 1 to 17), output `law_hint` as an integer; otherwise null.

Output strictly valid JSON with this format:
{
  "standalone_query": "Fully resolved English search query",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "law_hint": 12
}
"""


class QueryRewriter:
    """Rewrites conversational queries into standalone English retrieval queries."""

    def __init__(self, model: str = settings.model_chat):
        self.model = model

    async def rewrite(
        self,
        query: str,
        history: list[dict[str, str]] | None = None,
    ) -> RewriteResult:
        """Rewrite latest query with conversational history."""
        # If no history and query is already clean English, can do fast pass or still extract keywords
        history_msgs = history or []

        history_formatted = "\n".join(
            f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
            for msg in history_msgs[-6:]  # Keep last 3 exchanges (6 messages)
        )

        user_content = f"""CHAT HISTORY:
{history_formatted if history_formatted else "No previous history."}

LATEST USER MESSAGE:
{query}
"""

        messages = [
            {"role": "system", "content": REWRITE_PROMPT},
            {"role": "user", "content": user_content},
        ]

        try:
            raw = await chat_client.complete(
                messages=messages,
                model=self.model,
                temperature=0.0,
                max_tokens=180,
                response_format={"type": "json_object"},
            )
            data = json.loads(raw)
            result = RewriteResult.model_validate(data)
            logger.info(
                f"Rewrote query: '{query[:30]}...' -> '{result.standalone_query[:40]}...' (law_hint={result.law_hint})",
                extra={"stage": "rewrite"},
            )
            return result

        except Exception as exc:
            logger.warning(f"Query rewrite failed ({exc}); falling back to raw query")
            clean_keywords = [
                w.lower() for w in re.findall(r"\b\w{3,}\b", query) if not w.isdigit()
            ][:5]
            return RewriteResult(
                standalone_query=query,
                keywords=clean_keywords,
                law_hint=None,
            )


rewriter = QueryRewriter()
