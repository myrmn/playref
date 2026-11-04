# RUN EVALUATION

Run the evaluation suite (`eval/run_eval.py`) against the current build.
1. Show the exact command and config (models, top_k, edition).
2. Output metrics: retrieval recall@6, citation accuracy, faithfulness, abstention accuracy, language match, latency p50/p95.
3. Compare to the previous report in `eval/reports/` and highlight regressions.
4. List the 10 worst-performing items with the failing stage (retrieval, rerank, generation, citation) and a hypothesis for each.
5. Save the Markdown report in `eval/reports/` and summarize in `docs/PROGRESS.md`.
Do not change code unless I ask; just measure and diagnose.
