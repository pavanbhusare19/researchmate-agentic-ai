import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()
ROOT = Path(__file__).parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
TRACE_FILE = LOG_DIR / "agent_traces.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("researchmate")


@tool
def calculate(expression: str) -> str:
    """Calculate a basic arithmetic expression. Use numbers and +, -, *, /, //, %, **, and parentheses only."""
    import ast
    import operator

    operators = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Exponent is too large.")
            return operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
            return operators[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic is allowed.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree)
        return str(result)
    except Exception as exc:
        return f"Calculation error: {exc}"


@tool
def save_research_note(title: str, note: str) -> str:
    """Save a short research note to the local notes/research_notes.md file. Use this when the user asks to save or record findings."""
    notes_dir = ROOT / "notes"
    notes_dir.mkdir(exist_ok=True)
    target = notes_dir / "research_notes.md"
    with target.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title.strip()}\n\n{note.strip()}\n")
    return f"Saved note to {target.relative_to(ROOT)}."


def build_agent():
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    if not tavily_key:
        raise RuntimeError("TAVILY_API_KEY is missing. Add it to your .env file.")

    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    model = ChatGroq(model=model_name, temperature=0)
    search = TavilySearch(max_results=5)
    tools = [search, calculate, save_research_note]
    system_prompt = """You are ResearchMate, a careful research and calculation assistant.
CUSTOM BEHAVIOUR:
- For questions about current facts, recent developments, or sources, use the web search tool before answering.
- For arithmetic, use the calculate tool instead of mental calculation.
- If the user asks to save or record a finding, use save_research_note.
- For multi-step questions, do the required steps in order, then provide a concise answer.
- Clearly distinguish sourced facts from your own explanation. Never invent sources or claim a search happened if it did not.
- If evidence is insufficient or a tool fails, say so honestly.
- End with a short "Steps taken" section naming the tools actually used."""
    return create_agent(model=model, tools=tools, system_prompt=system_prompt)


def _extract_text(result):
    messages = result.get("messages", [])
    if not messages:
        return str(result)
    content = messages[-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(part.get("text", part)) if isinstance(part, dict) else str(part) for part in content)
    return str(content)


def _tool_events(result):
    events = []
    for msg in result.get("messages", []):
        tool_calls = getattr(msg, "tool_calls", None) or []
        for call in tool_calls:
            events.append({
                "event": "tool_call",
                "tool": call.get("name", "unknown"),
                "input": call.get("args", {}),
                "reason": "Selected by the agent to complete the user request."
            })
        if getattr(msg, "type", "") == "tool":
            events.append({
                "event": "tool_result",
                "tool": getattr(msg, "name", "unknown"),
                "output_preview": str(getattr(msg, "content", ""))[:500]
            })
    return events


def run_agent(question: str):
    agent = build_agent()
    started = datetime.now().astimezone().isoformat()
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    answer = _extract_text(result)
    events = _tool_events(result)
    record = {
        "timestamp": started,
        "question": question,
        "tool_trace": events,
        "answer": answer
    }
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    for event in events:
        logger.info("TRACE %s", json.dumps(event, ensure_ascii=False))
    return answer, events


def main():
    print("\nResearchMate — Agentic AI Workflow")
    print("Tools: web search, calculator, research-note saver")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            continue
        try:
            answer, events = run_agent(question)
            print("\nResearchMate:", answer)
            print("\nTool trace:")
            if not events:
                print("- No tools were called for this request.")
            for event in events:
                print("-", json.dumps(event, ensure_ascii=False))
            print()
        except Exception as exc:
            logger.exception("Agent run failed")
            print(f"Error: {exc}\n")


if __name__ == "__main__":
    main()
