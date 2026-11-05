"""Grounded generation pipeline with JSON output, streaming, and citation validation."""

import json
import re
from collections.abc import AsyncGenerator
from typing import Any

from pydantic import ValidationError

from backend.app.config import settings
from backend.app.llm.chat import chat_client
from backend.app.logger import logger
from backend.app.rag.citations import CitationValidator, PlayRefAnswer
from backend.app.rag.retrieve import ScoredChunk

SYSTEM_PROMPT = """You are PlayRef, an intelligent football Laws of the Game assistant.

RULES:
- Answer ONLY from the provided context passages. If they do not cover it, clearly state that the official IFAB Laws do not cover this specific scenario.
- Never give a definitive refereeing verdict (do NOT say "This IS a penalty" or "The referee must show a red card"). Always frame answers around applicable Laws and possible interpretations.
- Highlight areas of referee discretion (e.g., careless vs reckless vs excessive force, natural position vs deliberate movement, deflection vs deliberate play).
- If crucial facts are missing (e.g. ball position, contact point, intent, on or off field), set `needs_more_info: true`, list the assumptions, and provide a polite `clarifying_question`.
- Every entry in `applicable_laws` MUST include the exact `chunk_id` from the provided context.
- You MUST answer in the requested language: {lang} (if Arabic, use Modern Standard Arabic; if French, French; if English, English).
- Strictly output valid JSON matching the schema below.
"""

ANSWER_SCHEMA_PROMPT = """Return a valid JSON object matching this schema:
{
  "short_answer": "Concise direct answer in {lang} explaining the rules and possible decisions",
  "applicable_laws": [
    {
      "citation": "Law N - Section Title",
      "chunk_id": "exact_chunk_id_from_context",
      "quote_or_summary": "Rule excerpt or summary"
    }
  ],
  "interpretations": ["Interpretation point 1", "Interpretation point 2"],
  "what_would_change_the_decision": ["Factor 1 that alters sanction or restart", "Factor 2"],
  "assumptions": ["Assumption made about missing facts"],
  "needs_more_info": false,
  "clarifying_question": null,
  "language": "{lang}"
}
"""


def format_context(scored_chunks: list[ScoredChunk]) -> str:
    """Format retrieved chunks into tagged context blocks."""
    blocks = []
    for sc in scored_chunks:
        c = sc.chunk
        header = f"[{c.chunk_id} | Law {c.law_number} - {c.section_path} | page {c.page}]"
        blocks.append(f"{header}\n{c.clean_text}")
    return "\n\n---\n\n".join(blocks)


class GroundedGenerator:
    """Generates structured answers grounded in retrieved IFAB passages."""

    def __init__(self, model: str = settings.model_chat):
        self.model = model

    def _build_messages(
        self, query: str, scored_chunks: list[ScoredChunk], language: str
    ) -> list[dict[str, str]]:
        context_str = format_context(scored_chunks)
        sys_msg = SYSTEM_PROMPT.format(lang=language)
        schema_str = ANSWER_SCHEMA_PROMPT.replace("{lang}", language)

        user_content = f"""QUESTION:
{query}

CONTEXT PASSAGES:
{context_str}

{schema_str}
"""
        return [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_content},
        ]

    async def generate(
        self,
        query: str,
        scored_chunks: list[ScoredChunk],
        language: str = "en",
    ) -> PlayRefAnswer:
        messages = self._build_messages(query, scored_chunks, language)

        raw_output = await chat_client.complete(
            messages=messages,
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        parsed_answer: PlayRefAnswer | None = None
        try:
            data = json.loads(raw_output)
            parsed_answer = PlayRefAnswer.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as err:
            logger.warning(f"Malformed JSON from generator ({err}); retrying once with hint...")
            retry_messages = messages + [
                {"role": "assistant", "content": raw_output},
                {
                    "role": "user",
                    "content": f"Your response had a JSON/validation error: {err}. Output strictly valid JSON conforming to the schema.",
                },
            ]
            retry_raw = await chat_client.complete(
                messages=retry_messages,
                model=self.model,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            data = json.loads(retry_raw)
            parsed_answer = PlayRefAnswer.model_validate(data)

        # Server-side citation validation
        chunks = [sc.chunk for sc in scored_chunks]
        return CitationValidator.validate(parsed_answer, chunks)

    async def stream_generate(
        self,
        query: str,
        scored_chunks: list[ScoredChunk],
        language: str = "en",
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream the short answer deltas first, then yield the validated final answer payload."""
        messages = self._build_messages(query, scored_chunks, language)

        accumulated = []
        short_answer_extracted = ""
        stream_mode_active = True

        try:
            async for token in chat_client.stream(
                messages=messages,
                model=self.model,
                temperature=0.1,
            ):
                accumulated.append(token)
                full_text = "".join(accumulated)

                # Attempt to stream the content of "short_answer" as it gets generated
                if '"short_answer":' in full_text:
                    match = re.search(r'"short_answer"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)', full_text)
                    if match:
                        current_str = (
                            match.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
                        )
                        new_delta = current_str[len(short_answer_extracted) :]
                        if new_delta:
                            short_answer_extracted = current_str
                            yield {"event": "delta", "data": {"content": new_delta}}

        except Exception as exc:
            logger.warning(f"Streaming failed ({exc}); falling back to standard completion")
            stream_mode_active = False

        # Parse full accumulated text, or fetch via complete if streaming errored
        raw_final = "".join(accumulated)
        if not stream_mode_active or not raw_final.strip().endswith("}"):
            raw_final = await chat_client.complete(
                messages=messages,
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"},
            )

        try:
            # Clean possible markdown wrapping ```json ... ```
            clean_json = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", raw_final.strip(), flags=re.MULTILINE
            )
            data = json.loads(clean_json)
            parsed_answer = PlayRefAnswer.model_validate(data)
        except Exception:
            # Fallback structure
            parsed_answer = PlayRefAnswer(
                short_answer=short_answer_extracted
                or "Unable to parse complete structured response.",
                applicable_laws=[],
                interpretations=[],
                what_would_change_the_decision=[],
                assumptions=[],
                needs_more_info=False,
                language=language,
            )

        chunks = [sc.chunk for sc in scored_chunks]
        validated_answer = CitationValidator.validate(parsed_answer, chunks)

        yield {"event": "answer", "data": validated_answer.model_dump()}


generator = GroundedGenerator()
