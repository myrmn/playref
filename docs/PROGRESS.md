# PlayRef Progress Tracker

The agent updates this file. The user can read it anytime.

**Current phase:** Phase 3: Web UI
**Last updated:** 2026-11-05

## Phase status
| Phase | Status | Approved by user |
|---|---|---|
| 1 Core RAG (CLI) | APPROVED/DONE | yes |
| 2 Pipeline + API + eval | APPROVED/DONE | yes |
| 3 Web UI | AWAITING APPROVAL | no |
| 4 Image upload | NOT STARTED | no |
| 5 Video | NOT STARTED | no |
| 6 Advanced | NOT STARTED | no |

Status values: NOT STARTED | IN PROGRESS | AWAITING APPROVAL | APPROVED/DONE

## Task checklist (current phase: Phase 3 Web UI)
- [x] 1. Next.js App Router scaffold in `frontend/` with TypeScript, Tailwind CSS, Lucide icons, and design tokens from `DESIGN.md` (pitch green `#0F7B4B`, referee yellow `#F5C400`, card red `#D7263D`, dark mode)
- [x] 2. Core API client (`frontend/src/lib/api.ts`): SSE streaming parser for `/chat`, `/health`, `/conversations`, `/laws`, `/laws/{num}`, `/chunks/{id}`, `/feedback`
- [x] 3. Top navigation header: Wordmark/logo, Law browser view toggle, Language switcher (EN / FR / AR with RTL layout toggle), Theme toggle (Light/Dark mode)
- [x] 4. Empty chat / Home screen: Friendly headline, subline, large chat input with experimental upload button, 2x3 suggested prompt cards
- [x] 5. Active chat & streaming answer card: user message bubble, assistant card with short answer, streaming stage indicator, stop button, applicable law citation chips, collapsibles ("Possible interpretations", "What would change the decision", "Assumptions"), clarifying question interactive callout, feedback buttons (thumbs up/down, "Wrong law cited")
- [x] 6. Citation drawer / slide-over (desktop side drawer, mobile bottom sheet): Law badge, section path breadcrumb, exact chunk text, metadata (page, edition, source), "Open in Law browser" and "Copy citation" buttons
- [x] 7. Law browser view: searchable list of all 17 IFAB Laws with chunk counts, section tree viewer, reader pane with breadcrumb, and "Ask PlayRef about this section" quick prompt
- [x] 8. Modals & Edge Cases: "Wrong law cited" feedback modal, rate limit warning banner, off-topic redirect card, error state retry, disclaimer footer
- [x] 9. Full RTL mirroring & multi-language support (AR / FR / EN) with direction switching and localized UI strings
- [x] 10. Mobile responsiveness (390px viewport, bottom sheets, mobile nav) and accessibility checks

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-11-05 | Switch embeddings to local FastEmbed BGE-large (1024-dim) | Campus WAF on AIForge endpoint rate-limited repeated batch requests (Attack ID 20000008). Local inference avoids provider bans and runs offline with 0 latency. |
| 2026-11-05 | Graceful degradation on cross-encoder reranker | If the remote rerank endpoint times out or errors, RerankerService immediately falls back to hybrid retrieval order with synthetic scores without breaking generation. |
| 2026-11-05 | Singleton pattern on Qdrant local storage | QdrantLocal places file locks on data/qdrant_storage; singleton client ensures unified access across retriever, parent expander, and ingestion without lock contention. |
| 2026-11-05 | Law preamble isolation in chunker (`section_number="0"`) | Reset `current_raw_section = None` on new law headers so Law overview/preambles (e.g. scoring directly from goal kicks/throw-ins) do not leak into preceding laws. |
| 2026-11-05 | `lazy="selectin"` for SQLAlchemy async relationships | Eliminates `MissingGreenlet` exceptions during asynchronous history loading across SQLite and PostgreSQL. |
| 2026-11-05 | Next.js App Router for frontend in `frontend/` | Meets project spec & engineering rules with native SSR/client boundary, TypeScript, Tailwind CSS, Lucide icons, and zero-dependency SSE parsing. |
| 2026-11-05 | Dynamic RTL switching via `document.documentElement.dir` | Dynamically flips document layout, drawer slide animations, and Cairo font for Arabic (`ar`) while preserving LTR for English and French. |
| 2026-11-05 | Hermetic Qdrant mocking in unit tests | Avoids unit test failures when local vector storage has not yet undergone full ingestion by mocking `scroll()` and `count()` in `test_api.py`. |

## Known issues / tech debt
- Remote Qdrant runs in local embedded mode (data/qdrant_storage) when Docker Desktop service is inactive; Docker Compose configuration is ready for production container deployment.

## Open questions for the user
- Phase 3 is complete and ready for approval.
