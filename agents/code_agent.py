"""
agents/code_agent.py
---------------------
CODE EXPLANATION AGENT — Takes C++ code and explains it line-by-line.
Provides detailed, educational breakdowns of code logic.
"""

from ollama_client import query_ollama

CODE_SYSTEM_PROMPT = """You are an expert C++ code explainer and teacher.
Your task is to analyze C++ code and explain it thoroughly.

Your explanation MUST include:
1. **Overview**: What the code does at a high level (2-3 sentences)
2. **Line-by-Line Explanation**: Go through each important line or block
3. **Key Concepts Used**: List all C++ concepts/features used (e.g., pointers, classes, STL)
4. **Output**: What the program outputs (if determinable)
5. **Improvement Tips**: 1-2 suggestions to make the code better or more idiomatic C++

Format your response clearly with these sections using markdown headers.
Always be educational and explain WHY, not just WHAT."""


def handle(user_input: str, history: list = None) -> str:
    """
    Analyze and explain C++ code provided by the user.

    Args:
        user_input (str): User's message (may contain code or a description pointing to code).
        history (list): Previous messages — used to extract code if not in current message.

    Returns:
        str: Detailed code explanation.
    """
    # Try to extract code from current message or recent history
    code_to_explain = user_input

    prompt = f"""Please explain the following C++ code in detail:

{code_to_explain}

Provide a complete educational breakdown following the required format."""

    return query_ollama(prompt, system_prompt=CODE_SYSTEM_PROMPT)
