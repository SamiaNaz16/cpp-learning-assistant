"""
agents/quiz_agent.py
---------------------
QUIZ GENERATION AGENT — Generates 10 MCQ questions on C++ topics
with options A, B, C, D and correct answers.
"""

from ollama_client import query_ollama

QUIZ_SYSTEM_PROMPT = """You are a professional C++ exam question creator.
Generate exactly 10 multiple choice questions (MCQs) on the requested C++ topic.

STRICT FORMAT — Follow this EXACTLY for each question:

Q1. [Question text here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
✅ Answer: [Correct letter]) [Correct option text]
📝 Explanation: [One sentence explaining why this answer is correct]

---

Q2. [Question text here]
...and so on until Q10.

Rules:
- Questions must vary in difficulty (3 easy, 4 medium, 3 hard)
- All options must be plausible (no obviously wrong distractors)
- Cover different aspects of the topic
- Code-based questions are encouraged
- Explanations must be educational and concise"""


def handle(user_input: str, history: list = None) -> str:
    """
    Generate a 10-question MCQ quiz on the requested C++ topic.

    Args:
        user_input (str): User's message specifying the quiz topic.
        history (list): Previous messages for context.

    Returns:
        str: Formatted 10-question MCQ quiz.
    """
    # Extract topic from input
    topic = user_input.lower()
    for kw in ["quiz on", "quiz about", "test on", "test about", "questions on",
                "questions about", "mcq on", "mcq about", "generate quiz"]:
        topic = topic.replace(kw, "").strip()

    if not topic or len(topic) < 3:
        topic = "C++ fundamentals"

    prompt = f"""Generate 10 MCQ questions on the C++ topic: "{topic}"

Follow the exact format specified. Make questions educational and progressively challenging."""

    return query_ollama(prompt, system_prompt=QUIZ_SYSTEM_PROMPT)
