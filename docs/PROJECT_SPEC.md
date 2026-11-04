# PlayRef: Project Spec

## Concept
An intelligent football assistant that helps fans understand the Laws of the Game, analyze match situations, and get answers grounded in official refereeing documents.

It must:
- Explain applicable Laws and cite the relevant ones.
- Analyze situations and explain **possible interpretations**.
- Treat image/video-based incident analysis as **experimental, never definitive**.

It must NOT:
- Declare official decisions ("this IS a penalty").
- Answer rules questions from model memory without retrieved context.

## Knowledge base
- IFAB Laws of the Game (17 Laws, latest edition; store edition in metadata).
- VAR Protocol and Practical Guidelines for Match Officials (optional collection).
- Hand-written "situation -> law" Q&A layer (synthetic, reviewed by the user).
- Glossary/definitions.

## Architecture
```
Client (web) --HTTPS/SSE--> FastAPI
  1. Router (Llama-3.2-3B): intent + language
       intents: rules_question | scenario | media | off_topic
  2. Media pipeline (if upload): frames -> Gemma-3-4B -> JSON observations
       -> (optional) Qwen3.6-27B neutral scenario description
  3. Rewrite (Qwen3.6-35B-A3B): standalone English query + keywords, uses history
  4. Hybrid retrieval (BGE-M3 dense+sparse) in Qdrant -> top 30
  5. Rerank (BGE-Reranker-v2-m3) -> top 5-6
  6. Grounded generation (Qwen3.6-35B-A3B) -> structured JSON
  7. Citation validation (server-side)
Storage: Qdrant (vectors), Postgres (chats, feedback), Redis (rate limit/cache), MinIO (uploads)
```

## Models (see docs/API_CONTRACTS.md for endpoints)
| Task | Model |
|---|---|
| Routing / language detection | Llama-3.2-3B |
| Embeddings | BGE-M3 |
| Reranking | BGE-Reranker-v2-m3 |
| Rewrite + final answer | Qwen3.6-35B-A3B |
| Per-frame vision | Gemma-3-4B-IT |
| Multi-frame reasoning | Qwen3.6-27B |
| OCR (only if scanned sources) | Unlimited-OCR |

## Ingestion
- Extract with PyMuPDF; keep headings hierarchy: `Law N > Title > Section > Sub-section`.
- Structure-aware chunks of ~200-500 tokens, never crossing a heading.
- Prepend section path to the text before embedding.
- Metadata per chunk:
```json
{"chunk_id":"law12-s1-handball-003","law_number":12,"law_title":"Fouls and Misconduct",
 "section_path":"1. Direct free kick > Handball","edition":"2026/27","page":104,
 "source":"IFAB Laws of the Game","lang":"en","parent_id":"law12-s1"}
```
- Parent lookup: expand a retrieved sub-clause with its parent when helpful.
- Diagrams (e.g. offside) are stored as page-image references, not embedded.

## Answer contract (JSON from the generator)
```json
{
  "short_answer": "...",
  "applicable_laws": [{"citation":"Law 12 - Handball","chunk_id":"...","quote_or_summary":"..."}],
  "interpretations": ["..."],
  "what_would_change_the_decision": ["..."],
  "assumptions": ["..."],
  "needs_more_info": false,
  "clarifying_question": null,
  "language": "en"
}
```
Citation validator: every `chunk_id` must be in the retrieved set; otherwise remove the citation and log a warning.

## System prompt (generator)
```
You are PlayRef, a football Laws of the Game assistant.
RULES:
- Answer ONLY from the provided context passages. If they do not cover it, say so.
- Cite every claim as [Law N - Section]. Never invent law numbers.
- Never give a definitive refereeing verdict. Explain which Laws apply and the possible
  interpretations, noting where referee discretion applies (careless/reckless/excessive force,
  deliberate, etc.).
- If key facts are missing (location, ball position, intent), ask or list assumptions.
- Reply in the user's language: {lang}.
FORMAT: 1) Short answer 2) Applicable Laws 3) Possible interpretations 4) What would change the decision
```

## Media analysis principle
VLMs describe, they do not judge. Pipeline: **perception -> text observations -> same RAG pipeline**.
Vision prompt rule: "Describe only what is visible. Do not judge fouls. If unsure, say 'unclear'."
Observation JSON: location, ball_visible, ball_contact, arm_position, players_involved,
contact_between_players, overlay_text, uncertainty[].
Offside geometry (YOLO + homography) is a Phase 6 research spike, not part of the chatbot core.

## Frontend
Chat with streaming, citation chips + side drawer showing exact rule text/page, expandable
"Possible interpretations", upload button with "Experimental" badge, suggested prompts,
AR/FR/EN toggle with RTL, feedback buttons (thumbs + "wrong law cited"), Law browser sidebar.

## Evaluation
Golden set of 100-200 questions (rules, scenarios, AR/FR/EN, trap questions).
Metrics: retrieval recall@6, citation accuracy, faithfulness (LLM judge), abstention rate.
