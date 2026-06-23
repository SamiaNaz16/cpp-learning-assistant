"""
agents/debug_agent.py
----------------------
DEBUGGING AGENT — Detects errors in C++ code, explains them,
and provides corrected, working code.
"""

from ollama_client import query_ollama

DEBUG_SYSTEM_PROMPT = """You are an expert C++ debugger and compiler specialist.
Your task is to find ALL errors in C++ code and fix them.

Your response MUST follow this exact structure:

## 🔍 Error Analysis
List every error found (syntax, logical, runtime, compilation errors).
For each error, specify:
- **Error Type**: (Syntax / Logical / Runtime / Compilation)
- **Location**: Line number or code block where error occurs
- **Description**: What is wrong and WHY it is an error

## ✅ Corrected Code
Provide the complete corrected C++ code in a properly formatted code block.

## 📚 Explanation of Fixes
Explain each fix made, teaching the user what was wrong and the correct C++ approach.

## 💡 Prevention Tips
Give 1-2 tips to avoid similar errors in the future.

Be thorough. If the code has no errors, say so clearly and explain why the code is correct."""


def handle(user_input: str, history: list = None) -> str:
    """
    Debug C++ code provided by the user.

    Args:
        user_input (str): The user's message containing buggy C++ code.
        history (list): Previous messages for additional context.

    Returns:
        str: Detailed debugging report with corrected code.
    """
    prompt = f"""Please debug the following C++ code. Find all errors and provide the corrected version:

{user_input}

Follow the required structured format for your debugging report."""

    return query_ollama(prompt, system_prompt=DEBUG_SYSTEM_PROMPT)
