/**
 * script.js
 * ----------
 * Frontend logic for the Agentic AI C++ Learning Assistant.
 * Handles mode switching, message sending, rendering, and animations.
 */

// ── State ──────────────────────────────────────────────────────────────
let currentMode = 'chat';
let sessionId = localStorage.getItem('cpp_session_id') || generateSessionId();
let isLoading = false;
let messageHistory = JSON.parse(localStorage.getItem('cpp_chat_history') || '[]');

localStorage.setItem('cpp_session_id', sessionId);

// Mode configuration
const MODES = {
  chat: {
    label: '<i class="bi bi-chat-dots me-2"></i>C++ Chat Assistant',
    placeholder: 'Ask anything about C++...',
    agent: 'Chat Agent',
    hint: 'Mode: <strong>Chat</strong>'
  },
  code: {
    label: '<i class="bi bi-code-slash me-2"></i>Code Explanation',
    placeholder: 'Describe what you want explained, or add notes above...',
    agent: 'Code Explanation Agent',
    hint: 'Mode: <strong>Code Explainer</strong>'
  },
  debug: {
    label: '<i class="bi bi-bug me-2"></i>C++ Debugger',
    placeholder: 'Describe the issue or just click Send to debug the code above...',
    agent: 'Debugging Agent',
    hint: 'Mode: <strong>Debugger</strong>'
  },
  quiz: {
    label: '<i class="bi bi-patch-question me-2"></i>Quiz Mode',
    placeholder: 'Or type a quiz request here...',
    agent: 'Quiz Generation Agent',
    hint: 'Mode: <strong>Quiz</strong>'
  },
  recommend: {
    label: '<i class="bi bi-lightbulb me-2"></i>Learning Recommendations',
    placeholder: 'What C++ topics have you studied? What are your goals?',
    agent: 'Learning Recommendation Agent',
    hint: 'Mode: <strong>Recommendations</strong>'
  }
};

// ── Session ID ──────────────────────────────────────────────────────────
function generateSessionId() {
  return 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

// ── Mode Switching ──────────────────────────────────────────────────────
function setMode(mode) {
  currentMode = mode;
  const config = MODES[mode];

  // Update nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`btn-${mode}`)?.classList.add('active');

  // Update topbar
  document.getElementById('topbarTitle').innerHTML = config.label;
  document.getElementById('agentPill').innerHTML =
    `<span class="pulse-dot"></span>${config.agent}`;

  // Update placeholder
  document.getElementById('messageInput').placeholder = config.placeholder;

  // Update hint
  document.getElementById('modeHint').innerHTML = config.hint;

  // Show/hide panels
  const codePanel = document.getElementById('codePanel');
  const quizPanel = document.getElementById('quizPanel');

  codePanel.style.display = (mode === 'code' || mode === 'debug') ? 'block' : 'none';
  quizPanel.style.display = mode === 'quiz' ? 'block' : 'none';

  // Update code panel label
  if (mode === 'code') {
    document.getElementById('codePanelLabel').innerHTML =
      '<i class="bi bi-code-slash"></i> Paste your C++ code to explain';
  } else if (mode === 'debug') {
    document.getElementById('codePanelLabel').innerHTML =
      '<i class="bi bi-bug"></i> Paste your buggy C++ code here';
  }

  // Close sidebar on mobile
  if (window.innerWidth < 768) {
    document.getElementById('sidebar').classList.remove('open');
  }
}

function focusInput() {
  document.getElementById('messageInput').focus();
}

// ── Sidebar Toggle ──────────────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ── Key Handling ────────────────────────────────────────────────────────
function handleKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (!isLoading) sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 150) + 'px';
}

// ── Send Message ────────────────────────────────────────────────────────
async function sendMessage() {
  if (isLoading) return;

  const input = document.getElementById('messageInput');
  const codeInput = document.getElementById('codeInput');
  let userText = input.value.trim();

  // Compose message based on mode
  let messageToSend = '';
  let displayText = '';

  if (currentMode === 'code') {
    const code = codeInput.value.trim();
    if (!code && !userText) {
      showInputError('Please paste some C++ code to explain.');
      return;
    }
    if (code) {
      messageToSend = `Explain this C++ code:\n\`\`\`cpp\n${code}\n\`\`\``;
      if (userText) messageToSend += `\n\nAdditional context: ${userText}`;
      displayText = userText || '📋 Explain the pasted C++ code';
    } else {
      messageToSend = userText;
      displayText = userText;
    }
  } else if (currentMode === 'debug') {
    const code = codeInput.value.trim();
    if (!code && !userText) {
      showInputError('Please paste some C++ code to debug.');
      return;
    }
    if (code) {
      messageToSend = `Debug this C++ code:\n\`\`\`cpp\n${code}\n\`\`\``;
      if (userText) messageToSend += `\n\nIssue description: ${userText}`;
      displayText = userText || '🐛 Debug the pasted C++ code';
    } else {
      messageToSend = userText;
      displayText = userText;
    }
  } else {
    if (!userText) return;
    messageToSend = userText;
    displayText = userText;
  }

  // Clear inputs
  input.value = '';
  input.style.height = 'auto';

  // Hide welcome screen
  document.getElementById('welcomeScreen').style.display = 'none';

  // Add user message to UI
  addMessage('user', displayText);

  // Show typing indicator
  showTyping(MODES[currentMode].agent);
  setLoading(true);

  try {
    let response, data;

    if (currentMode === 'quiz') {
      // Quiz mode uses /chat endpoint with the message
      response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageToSend, session_id: sessionId })
      });
    } else {
      response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageToSend, session_id: sessionId })
      });
    }

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    data = await response.json();

    hideTyping();
    addMessage('assistant', data.response, data.agent_used, data.category);

    // Save to local history
    messageHistory.push({ role: 'user', content: displayText });
    messageHistory.push({ role: 'assistant', content: data.response });
    if (messageHistory.length > 40) messageHistory = messageHistory.slice(-40);
    localStorage.setItem('cpp_chat_history', JSON.stringify(messageHistory));

  } catch (err) {
    hideTyping();
    addMessage('assistant', formatError(err.message), 'System', 'error');
  } finally {
    setLoading(false);
  }
}

// ── Quick Messages ──────────────────────────────────────────────────────
function sendQuickMessage(text) {
  document.getElementById('messageInput').value = text;
  document.getElementById('welcomeScreen').style.display = 'none';
  sendMessage();
}

// ── Quiz Generation ──────────────────────────────────────────────────────
async function generateQuiz() {
  const topic = document.getElementById('quizTopic').value.trim() || 'C++ fundamentals';
  document.getElementById('messageInput').value = `Generate a quiz on ${topic}`;
  document.getElementById('welcomeScreen').style.display = 'none';
  await sendMessage();
}

// ── Message Rendering ──────────────────────────────────────────────────
function addMessage(role, content, agentUsed = '', category = '') {
  const list = document.getElementById('messageList');
  const row = document.createElement('div');
  row.className = `message-row ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';

  if (role === 'user') {
    bubble.textContent = content;
  } else {
    // Render markdown for assistant messages
    bubble.innerHTML = renderMarkdown(content);

    // Add copy buttons to code blocks
    bubble.querySelectorAll('pre').forEach(pre => {
      const btn = document.createElement('button');
      btn.className = 'copy-code-btn';
      btn.textContent = 'Copy';
      btn.onclick = () => {
        const code = pre.querySelector('code');
        navigator.clipboard.writeText(code?.textContent || '').then(() => {
          btn.textContent = 'Copied!';
          setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
        });
      };
      pre.style.position = 'relative';
      pre.appendChild(btn);
    });

    // Highlight code blocks
    bubble.querySelectorAll('pre code').forEach(block => {
      if (window.hljs) hljs.highlightElement(block);
    });
  }

  row.appendChild(bubble);

  // Add meta info for assistant messages
  if (role === 'assistant' && agentUsed) {
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    const tag = document.createElement('span');
    tag.className = 'agent-tag';
    tag.textContent = agentUsed;
    const time = document.createElement('span');
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    meta.appendChild(tag);
    meta.appendChild(time);
    row.appendChild(meta);
  }

  list.appendChild(row);
  scrollToBottom();
}

function renderMarkdown(text) {
  if (window.marked) {
    marked.setOptions({
      breaks: true,
      gfm: true,
      highlight: function(code, lang) {
        if (window.hljs && lang && hljs.getLanguage(lang)) {
          try { return hljs.highlight(code, { language: lang }).value; } catch {}
        }
        return code;
      }
    });
    return marked.parse(text);
  }
  // Fallback: basic formatting
  return text
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

function formatError(msg) {
  if (msg.includes('Cannot connect') || msg.includes('Failed to fetch')) {
    return `## ⚠️ Connection Error\n\nCannot reach Ollama. Please ensure:\n\n1. **Ollama is running**: Open a terminal and run \`ollama serve\`\n2. **Phi-3 is downloaded**: Run \`ollama pull phi3\`\n3. **Port 11434 is open**: Ollama should run on http://localhost:11434\n\nThen refresh this page and try again.`;
  }
  return `## ❌ Error\n\n${msg}\n\nPlease try again.`;
}

// ── Typing Indicator ────────────────────────────────────────────────────
function showTyping(agentName) {
  const indicator = document.getElementById('typingIndicator');
  document.getElementById('typingAgentLabel').textContent = agentName;
  indicator.style.display = 'block';
  scrollToBottom();
}

function hideTyping() {
  document.getElementById('typingIndicator').style.display = 'none';
}

// ── Utilities ───────────────────────────────────────────────────────────
function setLoading(val) {
  isLoading = val;
  const btn = document.getElementById('sendBtn');
  btn.disabled = val;
  if (val) {
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
  } else {
    btn.innerHTML = '<i class="bi bi-send-fill"></i>';
  }
}

function scrollToBottom() {
  const container = document.getElementById('chatContainer');
  setTimeout(() => {
    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
  }, 50);
}

function showInputError(msg) {
  const input = document.getElementById('messageInput');
  input.placeholder = `⚠️ ${msg}`;
  setTimeout(() => {
    input.placeholder = MODES[currentMode].placeholder;
  }, 3000);
}

function clearCodePanel() {
  document.getElementById('codeInput').value = '';
}

async function clearChat() {
  if (!confirm('Clear all chat history?')) return;
  document.getElementById('messageList').innerHTML = '';
  document.getElementById('welcomeScreen').style.display = 'block';
  messageHistory = [];
  localStorage.removeItem('cpp_chat_history');
  sessionId = generateSessionId();
  localStorage.setItem('cpp_session_id', sessionId);

  try {
    await fetch('/clear-history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
  } catch {}
}

// ── Restore chat history on load ────────────────────────────────────────
function restoreHistory() {
  if (messageHistory.length > 0) {
    document.getElementById('welcomeScreen').style.display = 'none';
    // Show last 10 messages
    const recent = messageHistory.slice(-10);
    recent.forEach(msg => {
      if (msg.role === 'user') {
        addMessage('user', msg.content);
      } else {
        addMessage('assistant', msg.content, 'Previous Session', '');
      }
    });
  }
}

// ── Init ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  restoreHistory();
  document.getElementById('messageInput').focus();
});
