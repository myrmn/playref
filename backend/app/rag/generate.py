"""Grounded generation pipeline with JSON output and citation validation."""

import json

from pydantic import ValidationError

from backend.app.config import settings
from backend.app.llm.chat import chat_client
from backend.app.logger import logger
from backend.app.rag.citations import CitationValidator, PlayRefAnswer
from backend.app.rag.retrieve import ScoredChunk

SYSTEM_PROMPT = """You are PlayRef, an intelligent football Laws of the Game assistant.

RULES:
- Answer ONLY from the provided context passages. If they do not cover it, clearly say so.
- Never give a definitive refereeing verdict (e.g. do NOT say "This is definitely a red card" or "The referee must award a penalty").
- Explain which Laws apply and the possible interpretations, noting where referee discretion applies (e.g., careless vs reckless vs excessive force, deliberate touch vs deflection, natural position).
- If key facts are missing (e.g., location on field, ball position, player intent), list assumptions or set needs_more_info=true and provide a clarifying_question.
- Cite your sources in 'applicable_laws' using the exact chunk_id from the context passages.
- Reply strictly in JSON conforming to the requested schema.
- Reply in the language requested: {lang}.
"""

ANSWER_SCHEMA_PROMPT = """Return a valid JSON object matching this schema:
{
  "short_answer": "Concise summary explaining the relevant Laws and possible outcomes",
  "applicable_laws": [
    {
      "citation": "Law N - Section Title",
      "chunk_id": "exact_chunk_id_from_context",
      "quote_or_summary": "Direct relevant rule excerpt or summary"
    }
  ],
  "interpretations": ["Interpretation point 1", "Interpretation point 2"],
  "what_would_change_the_decision": ["Factor 1 that changes outcome", "Factor 2"],
  "assumptions": ["Assumption 1"],
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

    async def generate(
        self,
        query: str,
        scored_chunks: list[ScoredChunk],
        language: str = "en",
    ) -> PlayRefAnswer:
        context_str = format_context(scored_chunks)
        sys_msg = SYSTEM_PROMPT.format(lang=language)

        schema_str = ANSWER_SCHEMA_PROMPT.replace("{lang}", language)
        user_content = f"""QUESTION:
{query}

CONTEXT PASSAGES:
{context_str}

{schema_str}
"""

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_content},
        ]

        # First attempt
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
                    "content": f"Your previous response had validation error: {err}. Please output valid JSON matching the schema.",
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
        validated_answer = CitationValidator.validate(parsed_answer, chunks)
        return validated_answer


generator = GroundedGenerator()
