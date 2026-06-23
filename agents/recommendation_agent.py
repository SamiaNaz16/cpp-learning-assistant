"""
agents/recommendation_agent.py
--------------------------------
LEARNING RECOMMENDATION AGENT — Analyzes user's query history
and recommends next C++ topics to study.
"""

from ollama_client import query_ollama

RECOMMEND_SYSTEM_PROMPT = """You are an expert C++ curriculum advisor and learning coach.
Based on the user's learning history and current query, suggest a personalized learning path.

Your response MUST include:

## 📊 Your Current Level Assessment
Briefly assess what the user seems to know based on their history.

## 🎯 Recommended Next Topics (Priority Order)
List 5-7 topics to study next, each with:
- **Topic Name**
- **Why**: One sentence on why this is the right next step
- **Estimated Time**: How long to master this topic
- **Key Concepts**: 3-4 bullet points of what to learn within this topic

## 📚 Suggested Learning Sequence
A numbered week-by-week or step-by-step plan.

## 🔗 Practice Recommendations
Suggest 2-3 types of projects or exercises to reinforce learning.

Be encouraging, specific, and base recommendations on actual C++ learning progressions."""


def handle(user_input: str, history: list = None) -> str:
    """
    Generate personalized C++ topic recommendations.

    Args:
        user_input (str): User's current request or question.
        history (list): List of previous queries to understand user's level.

    Returns:
        str: Personalized learning recommendations.
    """
    # Summarize history for context
    history_summary = ""
    if history:
        topics = [msg.get("content", "") for msg in history if msg.get("role") == "user"]
        if topics:
            history_summary = "User's previous questions/topics studied:\n"
            for i, t in enumerate(topics[-8:], 1):  # Last 8 user messages
                history_summary += f"{i}. {t[:100]}\n"

    prompt = f"""User's request: {user_input}

{history_summary if history_summary else "No previous history — treat as a beginner."}

Based on this information, provide personalized C++ learning recommendations."""

    return query_ollama(prompt, system_prompt=RECOMMEND_SYSTEM_PROMPT)
