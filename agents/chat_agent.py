"""
agents/chat_agent.py
---------------------
CHAT AGENT — Handles general C++ questions and theory.
Uses Ollama Phi-3 to generate educational, detailed responses.
"""

from ollama_client import query_ollama

CHAT_SYSTEM_PROMPT = """You are an expert C++ tutor and professor with 20 years of experience.
Your role is to answer C++ questions clearly, accurately, and in an educational manner.

Guidelines:
- Explain concepts with simple analogies when helpful
- Always provide small code examples to illustrate theory
- Use proper C++ syntax in all code examples
- Format code blocks using triple backticks with cpp tag
- Be encouraging and supportive to learners
- If the question is not about C++, gently redirect to C++ topics
- Structure responses with clear headings when appropriate"""


def handle(user_input: str, history: list = None) -> str:
    """
    Process a general C++ question and return an educational response.

    Args:
        user_input (str): The user's question.
        history (list): Optional list of previous messages for context.

    Returns:
        str: AI-generated educational response.
    """
    # Build context from history if available
    context = ""
    if history:
        recent = history[-4:]  # Use last 4 messages for context
        context = "Previous conversation context:\n"
        for msg in recent:
            role = "User" if msg.get("role") == "user" else "Assistant"
            context += f"{role}: {msg.get('content', '')}\n"
        context += "\nCurrent question:\n"

    prompt = f"{context}{user_input}"
    return query_ollama(prompt, system_prompt=CHAT_SYSTEM_PROMPT)
