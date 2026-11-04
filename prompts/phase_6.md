# PHASE 6: Advanced features

Precondition: Phase 5 approved by me. Set `docs/PROGRESS.md`: Phase 6 = IN PROGRESS. Re-read `AGENTS.md` and `docs/PROGRESS.md`.

## Step 0: Choose the order WITH me
Present these options with effort (S/M/L), value, and risk. Recommend an order, then WAIT for my choice. Work on one option at a time and run the Phase Gate after each option (each option = a mini-phase: report, then ask approval before the next).

### Option A: VAR Protocol assistant (M)
Add the VAR Protocol / Practical Guidelines as a separate collection with its own metadata (`source=var_protocol`). Router intent `var_question`. Answers explain what is reviewable (goals, penalties, direct red cards, mistaken identity) and what is not. Eval additions.

### Option B: Quiz mode (S/M)
`POST /quiz` generates questions from retrieved Law chunks (multiple choice, with explanation and citation), difficulty levels, per-Law selection, answer checking, score tracking per session. Frontend quiz screen. Validate that every question is verifiable against a chunk.

### Option C: Offside geometry research spike (L, high risk)
Timeboxed feasibility study ONLY: user supplies a frame at the moment the ball is played; pipeline = player detection (YOLO) -> pitch line detection -> homography -> offside line overlay. Deliver a notebook/script, accuracy on sample images, honest feasibility report and recommendation. Do not integrate into the product unless I approve after the report. Label any output "visual aid, not an official decision".

### Option D: Admin dashboard (M)
Feedback review (wrong-law-cited queue), top failing questions, convert flagged cases into eval golden items, basic usage metrics. Simple auth for admin only.

### Option E: Deployment and ops (M)
Production Docker images, CI (lint, tests, eval gate), env management, reverse proxy + TLS, monitoring (logs, latency, error rate), backups for Postgres/Qdrant, cost/usage report, security review (rate limits, upload hardening, secrets).

### Option F: Content refresh pipeline (S)
Script to ingest a new Laws edition (July update), diff chunks between editions, re-run eval, version collections so old editions remain queryable.

## For each option you work on
1. Short plan + acceptance criteria (agreed with me).
2. Implementation with tests and eval impact.
3. Mini Phase Report and gate question:
"Option X is complete. Which option next, or are we done? (reply with the option or "done")"

## When I say "done"
Final project report: architecture as built, how to run/deploy, eval results, known limitations, recommended next steps. Update `docs/PROGRESS.md` and `README` of the repo.
