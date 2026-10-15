
import os
from flask import Flask, request, jsonify, render_template_string
from app import run_agent

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ResearchMate | Agentic AI Workflow</title>
<style>
body {
  font-family: Arial, sans-serif;
  max-width: 900px;
  margin: 35px auto;
  padding: 20px;
  background: #f5f7fb;
  color: #172033;
}
section {
  background: white;
  padding: 20px;
  margin: 18px 0;
  border-radius: 12px;
  border: 1px solid #dce3ed;
}
h1 { margin-bottom: 8px; }
textarea {
  width: 100%;
  min-height: 115px;
  box-sizing: border-box;
  padding: 12px;
  font-size: 15px;
}
button {
  padding: 12px 20px;
  margin-top: 12px;
  cursor: pointer;
}
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #f3f5f8;
  padding: 14px;
  border-radius: 8px;
}
.tool { border-left: 4px solid #64748b; padding-left: 12px; }
.small { color: #526078; line-height: 1.6; }
</style>
</head>
<body>
<h1>ResearchMate: Agentic AI Workflow</h1>
<p class="small">
An AI research agent that can select tools, execute actions,
inspect tool results, and produce a final response.
</p>

<section>
<h2>Available Agent Tools</h2>
<ul>
<li><b>Web Search:</b> retrieve information and sources.</li>
<li><b>Calculator:</b> perform arithmetic through a tool.</li>
<li><b>Research Note Saver:</b> save requested findings.</li>
</ul>
<p class="small">
The agent selects tools according to the request. Not every
request requires every tool.
</p>
</section>

<section>
<h2>Run an Agent Workflow</h2>
<p>Enter a goal for ResearchMate to complete.</p>
<form id="chat">
<textarea id="question" maxlength="4000" required
placeholder="Example: Search the web for the latest Python release, summarize the findings, calculate how many years since 1991, and save a research note with the findings."></textarea>
<button id="submit" type="submit">Run Agent</button>
</form>
<p id="status" class="small">Ready.</p>
</section>

<section>
<h2>Final Answer</h2>
<pre id="answer">Your answer will appear here.</pre>
</section>

<section>
<h2>Execution Trace</h2>
<p class="small">
Actual tool calls and results returned by the agent are shown here.
</p>
<div id="trace">No execution yet.</div>
</section>

<script>
const form = document.getElementById("chat");
const statusBox = document.getElementById("status");
const answerBox = document.getElementById("answer");
const traceBox = document.getElementById("trace");
const submitButton = document.getElementById("submit");

form.addEventListener("submit", async function(e) {
  e.preventDefault();

  const question = document.getElementById("question").value.trim();
  if (!question) return;

  submitButton.disabled = true;
  statusBox.textContent = "Agent is planning and executing...";
  answerBox.textContent = "Working...";
  traceBox.textContent = "Waiting for execution events...";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question})
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Agent request failed.");
    }

    answerBox.textContent = data.answer || "No answer returned.";
    const events = data.tool_trace || [];

    if (events.length === 0) {
      traceBox.textContent =
        "No tool calls were recorded for this request.";
    } else {
      traceBox.replaceChildren();

      events.forEach((event, index) => {
        const card = document.createElement("div");
        card.className = "tool";

        const heading = document.createElement("h3");
        heading.textContent =
          (index + 1) + ". " +
          (event.event || "event") + " — " +
          (event.tool || "unknown tool");

        const details = document.createElement("pre");
        details.textContent = JSON.stringify(event, null, 2);

        card.append(heading, details);
        traceBox.append(card);
      });
    }

    statusBox.textContent =
      "Completed. Recorded tool events: " + events.length;
  } catch (error) {
    answerBox.textContent = error.message;
    statusBox.textContent = "Execution failed. Check server logs.";
    traceBox.textContent = "No complete trace available.";
  } finally {
    submitButton.disabled = false;
  }
});
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    if len(question) > 4000:
        return jsonify({"error": "Question is too long"}), 400

    try:
        answer, events = run_agent(question)
        return jsonify({
            "answer": answer,
            "tool_trace": events,
            "agent": "ResearchMate",
            "workflow": "tool-using agent"
        })
    except Exception:
        app.logger.exception("Agent request failed")
        return jsonify({
            "error": "Agent request failed; check server logs"
        }), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "ResearchMate",
        "agent_workflow": True,
        "tools": ["web_search", "calculate", "save_research_note"]
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
