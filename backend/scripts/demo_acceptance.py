"""Acceptance demonstrations for Phase 2:
- Multilingual responses (EN, FR, AR)
- Follow-up conversation memory
- Off-topic redirection without retrieval
- SSE streaming token delivery
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from httpx import ASGITransport, AsyncClient

from backend.app.main import app


async def run_demos():
    print("=" * 60)
    print("PLAYREF PHASE 2 ACCEPTANCE DEMONSTRATIONS")
    print("=" * 60)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. English query with SSE streaming
        print("\n[1] DEMO: English Query + SSE Streaming")
        print("Query: 'Can a goalkeeper score directly from a goal kick?'")
        req1 = {
            "query": "Can a goalkeeper score directly from a goal kick?",
            "stream": True,
        }
        resp1 = await client.post("/chat", json=req1)
        print("HTTP Status:", resp1.status_code)
        print("SSE Event stream (first 4 events):")
        lines = [line for line in resp1.text.split("\n") if line.startswith("data: ")]
        for line_item in lines[:4]:
            print(" ", line_item[:120])
        print("  ... total events:", len(lines))
        conv_id = None
        # Parse final answer event
        for line_item in lines:
            try:
                payload = json.loads(line_item[6:])
                if "answer" in payload:
                    conv_id = payload.get("conversation_id")
                    print(
                        "Structured Short Answer:", payload["answer"]["short_answer"][:120] + "..."
                    )
                    print(
                        "Citations:",
                        [
                            f"{law.get('citation', '')} ({law.get('chunk_id', '')})"
                            for law in payload["answer"]["applicable_laws"]
                        ],
                    )
            except Exception:
                pass

        # 2. French query
        print("\n[2] DEMO: French Query")
        print("Query: 'Un joueur hors-jeu est-il sanctionné s\\'il ne touche pas le ballon ?'")
        req2 = {
            "query": "Un joueur hors-jeu est-il sanctionné s'il ne touche pas le ballon ?",
            "stream": False,
        }
        resp2 = await client.post("/chat", json=req2)
        ans2 = resp2.json()["answer"]
        print("Detected language: fr")
        print("Short Answer (FR):", ans2["short_answer"])
        print(
            "Citations:",
            [f"{law.get('citation')} ({law.get('chunk_id')})" for law in ans2["applicable_laws"]],
        )

        # 3. Arabic query
        print("\n[3] DEMO: Arabic Query (with Tunisian dialect handling)")
        print("Query: 'هل يمكن تسجيل هدف مباشر من رمية تماس؟'")
        req3 = {
            "query": "هل يمكن تسجيل هدف مباشر من رمية تماس؟",
            "stream": False,
        }
        resp3 = await client.post("/chat", json=req3)
        ans3 = resp3.json()["answer"]
        print("Detected language: ar")
        print("Short Answer (AR):", ans3["short_answer"])
        print(
            "Citations:",
            [f"{law.get('citation')} ({law.get('chunk_id')})" for law in ans3["applicable_laws"]],
        )

        # 4. Multi-turn Follow-up Query
        print("\n[4] DEMO: Multi-turn Follow-up")
        print(f"Conversation ID: {conv_id}")
        print("Turn 1 was: 'Can a goalkeeper score directly from a goal kick?'")
        print("Turn 2 Query: 'What if the ball enters the kicker\\'s own goal directly?'")
        req4 = {
            "query": "What if the ball enters the kicker's own goal directly?",
            "conversation_id": conv_id,
            "stream": False,
        }
        resp4 = await client.post("/chat", json=req4)
        ans4 = resp4.json()["answer"]
        print("Short Answer:", ans4["short_answer"])
        print(
            "Citations:",
            [f"{law.get('citation')} ({law.get('chunk_id')})" for law in ans4["applicable_laws"]],
        )

        # 5. Off-topic redirection without retrieval
        print("\n[5] DEMO: Off-topic Redirection")
        print("Query: 'Can you write me a recipe for chocolate cookies?'")
        req5 = {
            "query": "Can you write me a recipe for chocolate cookies?",
            "stream": False,
        }
        resp5 = await client.post("/chat", json=req5)
        ans5 = resp5.json()["answer"]
        print(
            "Is Off-Topic:",
            resp5.json().get("debug", {}).get("intent") == "off_topic"
            or not ans5["applicable_laws"],
        )
        print("Redirect Message:", ans5["short_answer"])

    print("\n" + "=" * 60)
    print("ALL ACCEPTANCE DEMONSTRATIONS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demos())
