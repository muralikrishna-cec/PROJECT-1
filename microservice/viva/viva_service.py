from viva.keyword_extractor import extract_keywords
from viva.tinyllama_client import generate_with_gemini, generate_with_tinyllama
import random
import re


def generate_viva_questions(code: str, language: str, count: int = 5):
    """
    Generate viva questions + marks for given code and language.
    Priority: Gemini -> TinyLLaMA -> Fallback templates.
    """

    # --- Step 1: Try Gemini first (MCQ with answers) ---
    gemini_result = generate_with_gemini(code, language)
    if gemini_result and gemini_result.get("questions"):
        # ✅ Limit to exactly 'count' questions
        gemini_result["questions"] = gemini_result["questions"][:count]
        return gemini_result

    # --- Step 2: Extract keywords for fallback ---
    keywords = extract_keywords(code, language)
    if not keywords:
        keywords = [language, "functions", "loops", "variables"]

    # --- Step 3: Build prompt for TinyLLaMA ---
    prompt = (
        f"Generate exactly {count} viva questions for {language} code.\n"
        f"Concepts: {', '.join(keywords)}.\n"
        "Do NOT include answers.\n"
        "Start with: 'Marks: X' (where X is out of 10).\n"
        f"Then list the questions, one per line, numbered 1 to {count}."
    )

    result = generate_with_tinyllama(prompt)

    marks = 0
    questions = []

    # Case A: structured dict returned
    if isinstance(result, dict):
        marks = result.get("marks", 0)
        questions = result.get("questions", [])

    # Case B: plain text returned → parse it
    elif isinstance(result, str):
        match = re.search(r"Marks:\s*(\d+)", result)
        if match:
            marks = int(match.group(1))
        questions = re.findall(r"\d+\.\s*(.+)", result)

    # --- Step 4: Fallback templates if TinyLLaMA fails ---
    if not questions or len(questions) < count:
        base_templates = [
            "What is the purpose of {kw} in {language}?",
            "How does {kw} work in {language}?",
            "Can you give an example of using {kw} in {language}?",
            "Why is {kw} important in programming?",
            "What are common errors when using {kw} in {language}?"
        ]
        for kw in keywords:
            for template in base_templates:
                if len(questions) >= count:
                    break
                questions.append(template.format(kw=kw, language=language))

    # --- Step 5: Ensure exactly 'count' questions ---
    questions = list(dict.fromkeys(questions))[:count]

    if marks == 0:
        marks = random.randint(5, 9)

    return {
        "marks": marks,
        "questions": questions
    }
