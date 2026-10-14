import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from app import run_agent

load_dotenv()
ROOT = Path(__file__).parent
CASES_PATH = ROOT / "eval" / "eval_cases.json"
RESULTS_PATH = ROOT / "eval" / "latest_results.json"
REPORT_PATH = ROOT / "eval" / "EVALUATION_REPORT.md"


def main():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = []
    passed = 0
    print(f"Running {len(cases)} evaluation cases. This makes live LLM/search calls.")
    for index, case in enumerate(cases, start=1):
        print(f"\n[{index}/{len(cases)}] {case['id']}: {case['prompt']}")
        try:
            answer, events = run_agent(case["prompt"])
            used_tools = sorted({event["tool"] for event in events if event["event"] == "tool_call"})
            answer_lower = answer.lower()
            keyword_match = any(word.lower() in answer_lower for word in case.get("expected_any_keywords", []))
            required_tools = case.get("expected_tools", [])
            tools_match = all(tool_name in used_tools for tool_name in required_tools)
            is_pass = bool(tools_match and keyword_match)
            row = {
                "id": case["id"],
                "prompt": case["prompt"],
                "expected_tools": required_tools,
                "used_tools": used_tools,
                "expected_any_keywords": case.get("expected_any_keywords", []),
                "keyword_match": keyword_match,
                "tools_match": tools_match,
                "pass": is_pass,
                "answer": answer,
                "trace": events
            }
        except Exception as exc:
            row = {
                "id": case["id"], "prompt": case["prompt"],
                "expected_tools": case.get("expected_tools", []), "used_tools": [],
                "expected_any_keywords": case.get("expected_any_keywords", []),
                "keyword_match": False, "tools_match": False, "pass": False,
                "answer": "", "error": str(exc), "trace": []
            }
        results.append(row)
        passed += int(row["pass"])
        print(("PASS" if row["pass"] else "FAIL") + f" — tools={row['used_tools']}; keyword_match={row['keyword_match']}")
    total = len(results)
    rate = round((passed / total) * 100, 1) if total else 0
    payload = {
        "run_at": datetime.now().astimezone().isoformat(),
        "total": total, "passed": passed, "failed": total - passed,
        "pass_rate_percent": rate, "results": results
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# ResearchMate Evaluation Report", "",
        f"- Run time: {payload['run_at']}",
        f"- Test cases: {total}",
        f"- Passed: {passed}",
        f"- Failed: {total - passed}",
        f"- **Pass rate: {rate}%**", "",
        "## Results", "",
        "| Case | Result | Expected tools | Tools used | Keyword check |",
        "|---|---|---|---|---|"
    ]
    for row in results:
        lines.append(
            f"| {row['id']} | {'PASS' if row['pass'] else 'FAIL'} | "
            f"{', '.join(row['expected_tools']) or 'none'} | "
            f"{', '.join(row['used_tools']) or 'none'} | "
            f"{'pass' if row['keyword_match'] else 'fail'} |"
        )
    lines += ["", "## Failure analysis", ""]
    failures = [r for r in results if not r["pass"]]
    if failures:
        lines += ["Review these cases manually; failures can indicate tool-selection issues, output wording variation, or API/search errors.", ""]
        for row in failures:
            lines.append(f"- **{row['id']}**: {row.get('error') or 'Expected criteria not met.'}")
    else:
        lines.append("All cases passed the simple automated checks. Human review is still recommended.")
    lines += ["", "## Evaluation method", "",
        "A case passes when all required tools appear in the recorded trace and at least one expected keyword appears in the final answer. This is a lightweight heuristic, not a complete semantic quality score. Inspect the JSON output and traces before reporting results.",
        ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nPass rate: {rate}% ({passed}/{total})")
    print(f"Saved: {RESULTS_PATH.relative_to(ROOT)}")
    print(f"Saved: {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
