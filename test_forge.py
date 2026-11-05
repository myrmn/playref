import os
import sys

import httpx
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load variables from .env
load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv(
    "OPENAI_BASE_URL", "https://aiforge.esprit.tn/api/v1"
)
API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("MODEL_CHAT") or os.getenv("LLM_MODEL_MAIN", "Qwen3.6-35B-A3B")

print(f"Testing endpoint: {BASE_URL}")
print(f"Model: {MODEL}")
print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
print("-" * 50)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 50,
}

try:
    with httpx.Client(base_url=BASE_URL, headers=headers, timeout=15.0) as client:
        print("Sending 'hi' to /chat/completions ...")
        response = client.post("/chat/completions", json=payload)

        print(f"HTTP Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            print(f"Response from AIForge:\n{reply}")
        else:
            print("Error response:")
            print(response.text)
except Exception as e:
    print(f"Connection failed: {e}")
