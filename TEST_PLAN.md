# Evaluation plan

Run `python evaluate.py` to execute the 10 cases in `eval/eval_cases.json`.

The current pass rule is deterministic and intentionally simple:
1. All required tool names must appear in the trace.
2. At least one expected keyword must appear in the final response.

This harness evaluates basic tool selection and output presence, not full factual correctness. Inspect `eval/latest_results.json`, `eval/EVALUATION_REPORT.md`, and `logs/agent_traces.jsonl`. Report the measured pass rate from the latest run and describe failures honestly.
