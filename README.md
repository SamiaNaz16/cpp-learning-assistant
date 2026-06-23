# ⚡ Agentic AI Based Offline C++ Learning Assistant
### Powered by Ollama (Phi-3) | Final Year Project

---

## 📌 Project Overview

This is a **fully offline, agent-based AI tutoring system** for learning C++. It uses **Ollama with the Phi-3 model** running locally — no internet connection or external APIs are required after initial setup.

The system is architected around **6 specialized AI agents**, coordinated by a central **Query Router Agent** that intelligently dispatches user requests to the correct agent.

---

## 🏗️ Agent-Based Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              QUERY ROUTER AGENT                             │
│  • Analyzes user input using Phi-3                          │
│  • Classifies into: chat / code_explain / debug /           │
│                      quiz / recommend                       │
│  • Falls back to keyword matching if LLM is ambiguous       │
└──────┬────────┬──────────┬───────────┬──────────────────────┘
       │        │          │           │           │
       ▼        ▼          ▼           ▼           ▼
  ┌────────┐ ┌──────┐ ┌───────┐  ┌────────┐ ┌──────────────┐
  │  CHAT  │ │ CODE │ │ DEBUG │  │  QUIZ  │ │ RECOMMEND    │
  │ AGENT  │ │AGENT │ │ AGENT │  │ AGENT  │ │    AGENT     │
  └────────┘ └──────┘ └───────┘  └────────┘ └──────────────┘
       │        │          │           │           │
       └────────┴──────────┴───────────┴───────────┘
                          │
                          ▼
             ┌─────────────────────┐
             │  Ollama (Phi-3)     │
             │  localhost:11434    │
             └─────────────────────┘
                          │
                          ▼
                   RESPONSE TO USER
```

---

## 🤖 Agent Descriptions

| Agent | File | Role |
|-------|------|------|
| **Query Router Agent** | `agents/query_router_agent.py` | Central dispatcher — classifies all inputs |
| **Chat Agent** | `agents/chat_agent.py` | Handles C++ theory, concepts, how-tos |
| **Code Explanation Agent** | `agents/code_agent.py` | Line-by-line C++ code explanation |
| **Debugging Agent** | `agents/debug_agent.py` | Finds errors, explains fixes, provides corrected code |
| **Quiz Generation Agent** | `agents/quiz_agent.py` | Generates 10 MCQs with answers & explanations |
| **Learning Recommendation Agent** | `agents/recommendation_agent.py` | Personalized topic suggestions based on history |

---

## 📁 Project Structure

```
cpp_assistant/
│
├── app.py                          # Flask application — all routes
├── ollama_client.py                # Ollama HTTP client (phi3 integration)
│
├── agents/
│   ├── __init__.py
│   ├── query_router_agent.py       # ★ Central classifier & router
│   ├── chat_agent.py               # General C++ Q&A
│   ├── code_agent.py               # Code explanation
│   ├── debug_agent.py              # Bug detection & fixing
│   ├── quiz_agent.py               # MCQ quiz generation
│   └── recommendation_agent.py    # Learning path advisor
│
├── templates/
│   └── index.html                  # ChatGPT-style UI
│
├── static/
│   ├── style.css                   # Dark theme UI styles
│   └── script.js                   # Frontend logic & chat handling
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai) installed on your machine

### Step 1: Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:** Download from https://ollama.ai/download

### Step 2: Download the Phi-3 Model
```bash
ollama pull phi3
```
> This downloads ~2GB. Only needed once.

### Step 3: Start Ollama Server
```bash
ollama serve
```
> Keep this terminal open. Ollama runs at http://localhost:11434

### Step 4: Install Python Dependencies
```bash
cd cpp_assistant
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
python app.py
```

### Step 6: Open in Browser
```
http://localhost:5000
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main chat interface |
| POST | `/chat` | Universal chat endpoint (routes through all agents) |
| POST | `/explain-code` | Dedicated code explanation |
| POST | `/debug-code` | Dedicated code debugging |
| POST | `/generate-quiz` | Dedicated quiz generation |
| POST | `/recommend` | Learning recommendations |
| POST | `/clear-history` | Clear session history |
| GET | `/health` | Health check |

### Example: /chat Request
```json
POST /chat
{
  "message": "Explain pointers in C++",
  "session_id": "sess_abc123"
}
```

### Example: /chat Response
```json
{
  "response": "## Pointers in C++\n\nA pointer is...",
  "category": "chat",
  "agent_used": "Chat Agent",
  "session_id": "sess_abc123"
}
```

---

## 🖥️ Frontend Features

- **ChatGPT-style dark UI** with chat bubbles
- **5 mode sidebar**: Chat, Code Explainer, Debugger, Quiz, Recommendations
- **Code input panel** for pasting C++ code (in Code/Debug modes)
- **Markdown rendering** with syntax highlighting (highlight.js)
- **Copy button** on all code blocks
- **Typing animation** while AI responds
- **Session persistence** via localStorage
- **Responsive design** — works on mobile and desktop

---

## 🔒 Offline Capability

This system is **100% offline** after initial setup:
- No OpenAI API calls
- No Gemini, Claude, or any external LLM
- No data leaves your machine
- All processing happens locally via Ollama

---

## 🚨 Troubleshooting

**"Cannot connect to Ollama"**
→ Run `ollama serve` in a terminal

**"Model not found"**
→ Run `ollama pull phi3`

**Slow responses**
→ Phi-3 needs ~4GB RAM. Close other apps. First request is slow (model loading).

**Port 5000 already in use**
→ Change `port=5000` in `app.py` to another port (e.g. 5001)

---

## 📚 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 + Flask | Backend server & API |
| Ollama + Phi-3 | Local offline LLM |
| HTML/CSS/JavaScript | Frontend UI |
| Bootstrap 5 | Responsive layout |
| marked.js | Markdown rendering |
| highlight.js | Code syntax highlighting |

---

## 👨‍💻 Final Year Project Information

**Title:** Agentic AI Based Offline C++ Learning Assistant using Ollama (Phi-3)

**Key Contributions:**
1. True agent-based architecture with a central router
2. Fully offline AI capability (no external dependencies at runtime)
3. Multi-agent system with 5 specialized AI agents
4. Session-aware learning history for personalized recommendations
5. Production-quality code structure with full comments
