"""
agents/query_router_agent.py
-----------------------------
QUERY ROUTER AGENT — The central brain of the system.
Analyzes user input and classifies it into one of 5 categories,
then routes to the appropriate specialized agent.
"""

from ollama_client import query_ollama


# Classification categories
CATEGORY_CHAT = "chat"
CATEGORY_CODE_EXPLAIN = "code_explain"
CATEGORY_DEBUG = "debug"
CATEGORY_QUIZ = "quiz"
CATEGORY_RECOMMEND = "recommend"


ROUTER_SYSTEM_PROMPT = """You are a query classification agent for a C++ learning assistant.
Your ONLY job is to classify the user's input into exactly ONE of these categories:
- chat: General C++ theory questions, concepts, definitions, how-to questions
- code_explain: User wants an explanation of C++ code they have provided
- debug: User has C++ code with errors/bugs and wants it fixed
- quiz: User wants to take a quiz, test, or MCQs on C++ topics
- recommend: User wants topic suggestions, learning path, or what to study next

Respond with ONLY the category word. Nothing else. No explanation. No punctuation.
Just one word from: chat, code_explain, debug, quiz, recommend"""


def classify_query(user_input: str) -> str:
    """
    Use Ollama to classify the user's query into a category.
    Falls back to keyword-based classification if the model returns unexpected output.

    Args:
        user_input (str): The raw user input.

    Returns:
        str: One of the 5 category constants.
    """
    prompt = f"Classify this user input:\n\n{user_input}"
    raw_response = query_ollama(prompt, system_prompt=ROUTER_SYSTEM_PROMPT)

    # Clean and normalize the response
    classification = raw_response.strip().lower().split()[0] if raw_response.strip() else ""

    valid_categories = {CATEGORY_CHAT, CATEGORY_CODE_EXPLAIN, CATEGORY_DEBUG,
                        CATEGORY_QUIZ, CATEGORY_RECOMMEND}

    if classification in valid_categories:
        return classification

    # Fallback: keyword-based classification
    return _keyword_fallback(user_input)


def _keyword_fallback(user_input: str) -> str:
    """
    Simple keyword-based fallback classifier used when the LLM returns
    an unexpected response.
    """
    text = user_input.lower()

    quiz_keywords = ["quiz", "mcq", "test me", "question", "multiple choice", "exam"]
    debug_keywords = ["error", "bug", "fix", "not working", "crash", "segfault",
                      "undefined", "compile", "syntax error", "runtime error", "debug"]
    code_keywords = ["explain this code", "what does this code", "this function",
                     "#include", "int main", "cout", "cin", "class ", "void ", "return 0"]
    recommend_keywords = ["what should i learn", "suggest", "next topic",
                          "learning path", "roadmap", "recommend", "what to study"]

    for kw in quiz_keywords:
        if kw in text:
            return CATEGORY_QUIZ
    for kw in debug_keywords:
        if kw in text:
            return CATEGORY_DEBUG
    for kw in code_keywords:
        if kw in text:
            return CATEGORY_CODE_EXPLAIN
    for kw in recommend_keywords:
        if kw in text:
            return CATEGORY_RECOMMEND

    return CATEGORY_CHAT


def route(user_input: str, history: list = None) -> dict:
    """
    Main routing function. Classifies input and returns routing metadata.

    Args:
        user_input (str): The user's message.
        history (list): Optional list of previous queries for context.

    Returns:
        dict: Contains 'category' and 'input' keys.
    """
    category = classify_query(user_input)
    return {
        "category": category,
        "input": user_input,
        "history": history or []
    }
