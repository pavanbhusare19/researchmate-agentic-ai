# ResearchMate Evaluation Report

- Run time: 2026-10-14T20:17:09.226719+05:30
- Test cases: 10
- Passed: 10
- Failed: 0
- **Pass rate: 100.0%**

## Results

| Case | Result | Expected tools | Tools used | Keyword check |
|---|---|---|---|---|
| TC01 | PASS | calculate | calculate | pass |
| TC02 | PASS | calculate | calculate | pass |
| TC03 | PASS | calculate | calculate | pass |
| TC04 | PASS | tavily_search | tavily_search | pass |
| TC05 | PASS | tavily_search | tavily_search | pass |
| TC06 | PASS | tavily_search | tavily_search | pass |
| TC07 | PASS | save_research_note | save_research_note | pass |
| TC08 | PASS | tavily_search, calculate | calculate, tavily_search | pass |
| TC09 | PASS | calculate | calculate | pass |
| TC10 | PASS | tavily_search, calculate | calculate, tavily_search | pass |

## Failure analysis

All cases passed the simple automated checks. Human review is still recommended.

## Evaluation method

A case passes when all required tools appear in the recorded trace and at least one expected keyword appears in the final answer. This is a lightweight heuristic, not a complete semantic quality score. Inspect the JSON output and traces before reporting results.
