# ResearchMate — Agentic AI Workflow

ResearchMate is a LangChain-based agent that can search the web, calculate arithmetic, and save research notes. It includes a custom research-assistant persona, intermediate tool traces, and a 10-case evaluation harness.

## Features

- **Three tools:** Tavily web search, a restricted arithmetic calculator, and a local research-note saver.
- **Custom AI behaviour:** uses search for current facts, calculator for arithmetic, saves notes only when requested, and acknowledges uncertainty.
- **Multi-step tasks:** can search and calculate in the same request.
- **Trace logging:** records tool names, inputs, outputs, and a brief reason in `logs/agent_traces.jsonl`.
- **Evaluation:** `eval/eval_cases.json` includes 10 test cases; `python evaluate.py` records results and computes a pass rate.

## Setup

Requires Python 3.10+.

1. Create and activate a virtual environment.
   - Windows: `py -m venv .venv`
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
2. Install dependencies:
   `python -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Add your own `GROQ_API_KEY` and `TAVILY_API_KEY` to `.env`.
5. Run the agent:
   `python app.py`
6. Run the evaluation suite:
   `python evaluate.py`

Do not commit `.env` or share API keys.

## Evaluation methodology

A test passes when every required tool is present in the trace and at least one expected keyword appears in the final answer. The script saves `eval/latest_results.json` and `eval/EVALUATION_REPORT.md`.

**Important:** This is a lightweight automated heuristic, not a complete semantic quality evaluation. Search results and generated wording may vary. Review failed cases and inspect the traces. Run `python evaluate.py` before reporting a pass rate; do not claim an unrun or invented result.

## Customisation (AI-6)

The system prompt defines the ResearchMate persona and custom rules:
- use web search for current facts,
- use the calculator for arithmetic,
- save a note only when requested,
- state uncertainty honestly,
- report which tools were used.

## Limitations

- Web search requires a Tavily API key and internet access.
- Generation requires a Groq API key and a model available to that account.
- Search results can change, and the evaluation keyword checks can produce false positives or false negatives.
- The local note saver appends text to a Markdown file; it does not send email or modify external services.
- Tool traces show the tool calls and their inputs/outputs; the stated reason is a general explanation, not a hidden chain-of-thought transcript.

## Repository submission checklist

- [ ] Add your real evaluation report after running the tests.
- [ ] Inspect and explain any failed cases.
- [ ] Verify `.env` is ignored and API keys are not committed.
- [ ] Push the project to GitHub and submit the repository URL.
