# PRE-APPROVAL REVIEW

Before I approve the current phase, do a critical self-review. Be honest; do not defend the work.

1. Re-check every acceptance criterion in `docs/ROADMAP.md` for this phase and re-run the evidence now.
2. Review the code for: hardcoded values/secrets, missing error handling and timeouts, untested critical paths, duplicated code, unclear naming, missing type hints, logging gaps.
3. Check product rules from `AGENTS.md`: no definitive verdicts, grounded answers only, citations validated, experimental labeling for media, correct language.
4. Security/privacy: input validation, upload handling, rate limits, PII in logs.
5. List the top 5 risks and top 5 improvements ranked by impact, with effort estimates.
6. Fix anything critical now; list the rest as tech debt in `docs/PROGRESS.md`.
Output a short report. Do not start the next phase.
