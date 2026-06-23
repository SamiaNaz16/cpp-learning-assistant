"""
app.py
-------
Main Flask application for the Agentic AI C++ Learning Assistant.
All requests pass through the Query Router Agent before reaching
specialized agents.
"""

from flask import Flask, request, jsonify, render_template, session
import uuid
import os

# Import the central router and all agents
from agents.query_router_agent import route, CATEGORY_CHAT, CATEGORY_CODE_EXPLAIN, \
    CATEGORY_DEBUG, CATEGORY_QUIZ, CATEGORY_RECOMMEND
from agents import chat_agent, code_agent, debug_agent, quiz_agent, recommendation_agent

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cpp-assistant-fyp-2024-secret")

# In-memory session store (replace with DB for production)
chat_sessions = {}


# ─────────────────────────────────────────────
# Helper: Get or create session history
# ─────────────────────────────────────────────
def get_session_history(session_id: str) -> list:
    return chat_sessions.get(session_id, [])


def save_to_history(session_id: str, role: str, content: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({"role": role, "content": content})
    # Keep last 20 messages to avoid memory bloat
    if len(chat_sessions[session_id]) > 20:
        chat_sessions[session_id] = chat_sessions[session_id][-20:]


# ─────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the main chat interface."""
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


# ─────────────────────────────────────────────
# CORE ENDPOINT: /chat (routes through Query Router Agent)
# ─────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint. ALL messages go through the Query Router Agent
    which classifies and dispatches to the correct specialized agent.
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field."}), 400

    user_input = data["message"].strip()
    session_id = data.get("session_id", session.get("session_id", str(uuid.uuid4())))

    if not user_input:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Save user message to history
    save_to_history(session_id, "user", user_input)
    history = get_session_history(session_id)

    # ── STEP 1: Route through Query Router Agent ──
    routing = route(user_input, history=history)
    category = routing["category"]

    # ── STEP 2: Dispatch to specialized agent ──
    if category == CATEGORY_CODE_EXPLAIN:
        response = code_agent.handle(user_input, history)
        agent_used = "Code Explanation Agent"
    elif category == CATEGORY_DEBUG:
        response = debug_agent.handle(user_input, history)
        agent_used = "Debugging Agent"
    elif category == CATEGORY_QUIZ:
        response = quiz_agent.handle(user_input, history)
        agent_used = "Quiz Generation Agent"
    elif category == CATEGORY_RECOMMEND:
        response = recommendation_agent.handle(user_input, history)
        agent_used = "Learning Recommendation Agent"
    else:
        response = chat_agent.handle(user_input, history)
        agent_used = "Chat Agent"

    # Save assistant response to history
    save_to_history(session_id, "assistant", response)

    return jsonify({
        "response": response,
        "category": category,
        "agent_used": agent_used,
        "session_id": session_id
    })


# ─────────────────────────────────────────────
# DEDICATED ENDPOINTS (also pass through router)
# ─────────────────────────────────────────────
@app.route("/explain-code", methods=["POST"])
def explain_code():
    """Dedicated endpoint for code explanation — still uses the agent pipeline."""
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field."}), 400

    code = data["code"].strip()
    session_id = data.get("session_id", str(uuid.uuid4()))
    user_input = f"Explain this C++ code:\n{code}"

    save_to_history(session_id, "user", user_input)
    history = get_session_history(session_id)

    response = code_agent.handle(user_input, history)
    save_to_history(session_id, "assistant", response)

    return jsonify({
        "response": response,
        "agent_used": "Code Explanation Agent",
        "session_id": session_id
    })


@app.route("/debug-code", methods=["POST"])
def debug_code():
    """Dedicated endpoint for code debugging."""
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field."}), 400

    code = data["code"].strip()
    session_id = data.get("session_id", str(uuid.uuid4()))
    user_input = f"Debug this C++ code:\n{code}"

    save_to_history(session_id, "user", user_input)
    history = get_session_history(session_id)

    response = debug_agent.handle(user_input, history)
    save_to_history(session_id, "assistant", response)

    return jsonify({
        "response": response,
        "agent_used": "Debugging Agent",
        "session_id": session_id
    })


@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    """Dedicated endpoint for quiz generation."""
    data = request.get_json()
    topic = data.get("topic", "C++ fundamentals") if data else "C++ fundamentals"
    session_id = data.get("session_id", str(uuid.uuid4()))
    user_input = f"Generate a quiz on {topic}"

    save_to_history(session_id, "user", user_input)
    history = get_session_history(session_id)

    response = quiz_agent.handle(user_input, history)
    save_to_history(session_id, "assistant", response)

    return jsonify({
        "response": response,
        "agent_used": "Quiz Generation Agent",
        "session_id": session_id
    })


@app.route("/recommend", methods=["POST"])
def recommend():
    """Dedicated endpoint for learning recommendations."""
    data = request.get_json()
    session_id = data.get("session_id", str(uuid.uuid4())) if data else str(uuid.uuid4())
    user_input = data.get("message", "What should I learn next in C++?") if data else \
        "What should I learn next in C++?"

    save_to_history(session_id, "user", user_input)
    history = get_session_history(session_id)

    response = recommendation_agent.handle(user_input, history)
    save_to_history(session_id, "assistant", response)

    return jsonify({
        "response": response,
        "agent_used": "Learning Recommendation Agent",
        "session_id": session_id
    })


# ─────────────────────────────────────────────
# UTILITY ENDPOINTS
# ─────────────────────────────────────────────
@app.route("/clear-history", methods=["POST"])
def clear_history():
    """Clear chat history for a session."""
    data = request.get_json()
    session_id = data.get("session_id") if data else None
    if session_id and session_id in chat_sessions:
        chat_sessions[session_id] = []
    return jsonify({"message": "History cleared."})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "running", "model": "phi3", "ollama_url": "http://localhost:11434"})


if __name__ == "__main__":
    print("=" * 60)
    print("  Agentic AI C++ Learning Assistant")
    print("  Powered by Ollama (Phi-3) — Fully Offline")
    print("=" * 60)
    print("  Make sure Ollama is running: ollama serve")
    print("  Make sure Phi-3 is pulled: ollama pull phi3")
    print("  Server starting at: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
