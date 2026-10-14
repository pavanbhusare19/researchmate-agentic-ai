
import os
from flask import Flask, request, jsonify, render_template_string
from app import run_agent

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ResearchMate AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="font-family:Arial;max-width:800px;margin:40px auto;padding:20px">
    <h1>ResearchMate AI</h1>
    <form id="chat">
        <textarea id="question" placeholder="Ask a research question"
         required maxlength="4000"
         style="width:100%;height:100px"></textarea>
        <button type="submit">Ask</button>
    </form>
    <h3>Answer</h3>
    <pre id="answer">Your answer will appear here.</pre>
    <script>
    document.getElementById("chat").onsubmit = async function(e) {
        e.preventDefault();
        const output = document.getElementById("answer");
        output.textContent = "Thinking...";
        try {
            const r = await fetch("/api/chat", {
                method: "POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({
                    question: document.getElementById("question").value
                })
            });
            const data = await r.json();
            output.textContent = data.answer || data.error || "Request failed";
        } catch (e) {
            output.textContent = "Could not connect to server.";
        }
    };
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
        return jsonify({"answer": answer, "tool_trace": events})
    except Exception:
        app.logger.exception("Agent request failed")
        return jsonify({"error": "Agent request failed; check server logs"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
