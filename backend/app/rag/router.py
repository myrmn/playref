"""Query routing and language detection for PlayRef."""

import json
from typing import Literal

from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.llm.chat import chat_client
from backend.app.logger import logger

IntentType = Literal["rules_question", "scenario", "media", "off_topic"]
LangType = Literal["en", "fr", "ar", "other"]


class RouteResult(BaseModel):
    intent: IntentType = Field(default="scenario")
    lang: LangType = Field(default="en")
    is_off_topic: bool = Field(default=False)
    redirect_message: str | None = Field(default=None)


ROUTER_PROMPT = """You are the intent and language classification router for PlayRef, a football (soccer) Laws of the Game assistant.

Analyze the user's query and classify:
1. `intent`:
   - "rules_question": Direct question about IFAB laws, rules, measurements, referee powers, card sanctions, or restarts.
   - "scenario": Match situation, incident description, foul analysis, or "what if" hypothetical play.
   - "media": User refers to an uploaded photo, image, screenshot, or video clip.
   - "off_topic": Non-football questions (politics, cooking, other sports, coding, general knowledge, etc.).
2. `lang`:
   - "ar": Arabic (Standard Arabic, North African/Tunisian dialect, or Arabizi).
   - "fr": French.
   - "en": English.
   - "other": Any other language.
3. `is_off_topic`: true if intent is "off_topic", else false.
4. `redirect_message`: If off-topic, provide a polite redirect message in the user's language explaining you only assist with football Laws of the Game. If not off-topic, set to null.

Output strictly valid JSON with this format:
{
  "intent": "rules_question|scenario|media|off_topic",
  "lang": "en|fr|ar|other",
  "is_off_topic": false,
  "redirect_message": null
}
"""

OFF_TOPIC_DEFAULTS = {
    "ar": "مرحباً! أنا PlayRef، مساعد مخصص حصرياً لقوانين كرة القدم والتحكيم. كيف يمكنني مساعدتك في قوانين اللعبة؟",
    "fr": "Bonjour ! Je suis PlayRef, un assistant dédié exclusivement aux Lois du Jeu de football et à l'arbitrage. Comment puis-je vous aider sur les règles ?",
    "en": "Hello! I am PlayRef, an assistant dedicated exclusively to football (soccer) Laws of the Game. How can I help you with the rules?",
    "other": "Hello! I am PlayRef, an assistant dedicated exclusively to football (soccer) Laws of the Game. How can I help you with the rules?",
}


class QueryRouter:
    """Classifies user queries for intent and language."""

    def __init__(self, model: str = settings.model_router):
        self.model = model

    async def route(self, query: str) -> RouteResult:
        """Route a user query using fast classification model."""
        messages = [
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": query},
        ]

        try:
            raw = await chat_client.complete(
                messages=messages,
                model=self.model,
                temperature=0.0,
                max_tokens=150,
                response_format={"type": "json_object"},
            )
            data = json.loads(raw)
            # Normalize lang & intent if model returned piped alternatives like 'fr|en'
            if "lang" in data and isinstance(data["lang"], str):
                raw_lang = data["lang"].lower()
                for valid in ("ar", "fr", "en", "other"):
                    if valid in raw_lang:
                        data["lang"] = valid
                        break
                else:
                    data["lang"] = "other"

            if "intent" in data and isinstance(data["intent"], str):
                raw_intent = data["intent"].lower()
                for valid in ("rules_question", "scenario", "media", "off_topic"):
                    if valid in raw_intent:
                        data["intent"] = valid
                        break

            result = RouteResult.model_validate(data)

            # If off-topic but no redirect message provided by LLM, inject default
            if result.is_off_topic or result.intent == "off_topic":
                result.intent = "off_topic"
                result.is_off_topic = True
                if not result.redirect_message:
                    result.redirect_message = OFF_TOPIC_DEFAULTS.get(
                        result.lang, OFF_TOPIC_DEFAULTS["en"]
                    )

            logger.info(
                f"Routed query: intent={result.intent}, lang={result.lang}, off_topic={result.is_off_topic}",
                extra={"stage": "route"},
            )
            return result

        except Exception as exc:
            logger.warning(
                f"Router classification failed ({exc}); falling back to default scenario/en"
            )
            return RouteResult(intent="scenario", lang="en", is_off_topic=False)


router = QueryRouter()
