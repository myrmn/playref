# PHASE 3: Web UI (Next.js)

Precondition: Phase 2 approved by me. Set `docs/PROGRESS.md`: Phase 3 = IN PROGRESS. Re-read `AGENTS.md`, `docs/ROADMAP.md`, `docs/PROGRESS.md`.

## Goal
A polished, responsive chat web app on top of the existing API. No backend feature work except small additions the UI strictly needs (list them and tell me).

## Step 0
Ask me up front (one message, then wait): brand preferences (colors/logo, default pitch-green theme OK?), dark mode wanted?, default language, and deployment target.

## Stack
Next.js (App Router) + TypeScript + Tailwind + shadcn/ui or Radix, TanStack Query, `next-intl` (or similar) for AR/FR/EN with RTL, SSE consumption via fetch streaming.

## Tasks
1. Project scaffold in `frontend/`, typed API client generated from the backend OpenAPI schema, env config for API URL.
2. **Chat panel**: message list, streaming render, typing/stage indicator ("searching Laws" -> "checking" -> "writing"), markdown rendering, stop-generation button, conversation persistence via the API.
3. **Answer card**: Short answer, Applicable Laws as **citation chips**, expandable "Possible interpretations" and "What would change the decision", assumptions list, clarifying-question highlight with quick-reply input.
4. **Citation drawer**: clicking a chip loads `/chunks/{id}` and shows exact rule text, Law + section path, page number, edition, and a "Open in Law browser" link.
5. **Law browser**: sidebar/page listing the 17 Laws with search, section tree, deep links `/laws/12#handball`.
6. **Suggested prompts** on empty state ("Explain offside", "Is deliberate handball always a foul?", "What is DOGSO?").
7. **Language toggle** AR/FR/EN with full RTL support and persisted preference.
8. **Feedback**: thumbs up/down, "wrong law cited" option, optional comment, calls `/feedback`.
9. **Disclaimer**: persistent, subtle footer: "PlayRef explains the Laws and possible interpretations. It does not make official decisions."
10. **Upload button placeholder**: visible but disabled with tooltip "Coming soon (experimental)". No upload logic yet.
11. Responsive/mobile-first, keyboard accessible, ARIA roles, loading/empty/error states, rate-limit error message.
12. Tests: component tests for AnswerCard and CitationChip, one Playwright e2e of the main flow (against mocked or real backend).

## Out of scope
Image/video upload logic, auth, admin dashboard.

## Acceptance criteria
See Phase 3 in `docs/ROADMAP.md`. Provide screenshots (or Playwright traces) of: empty state, streaming answer, citation drawer, Arabic RTL view, mobile view.

## When done
Phase Report, update `docs/PROGRESS.md` to AWAITING APPROVAL, STOP and ask:
"Phase 3 is complete. Approve moving to Phase 4? (reply "approved" or list changes)"
