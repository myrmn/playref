# DEBUG HELPER

Something is wrong: <describe symptom, paste error/logs, or the question that gave a bad answer>

Debug systematically. Do not guess or rewrite broad areas.
1. Reproduce it with a minimal command/test and show the output.
2. If it is a bad RAG answer, run with `--debug` and show per stage: router result, rewritten query, retrieved chunks + scores, reranked chunks + scores, final context, raw model output, validated output.
3. Identify the failing stage and the root cause with evidence.
4. Propose the smallest fix, apply it, add a regression test (or an eval item), and show before/after.
5. Update `docs/PROGRESS.md` (known issues/decisions) if relevant.
Stay inside the current phase scope.
