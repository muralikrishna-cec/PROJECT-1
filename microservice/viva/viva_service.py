from viva.keyword_extractor import extract_keywords
from viva.tinyllama_client import generate_with_gemini, generate_with_tinyllama
import random
import re

def generate_viva_questions(code: str, language: str, count: int = 5):
    """
    Generate viva questions + marks for given code and language.
    Priority: Gemini -> TinyLLaMA -> Fallback MCQs.
    Returns structured JSON with MCQs.
    """

    # --- Step 1: Try Gemini first (MCQ with answers) ---
    gemini_result = generate_with_gemini(code, language, count)
    if gemini_result and gemini_result.get("questions"):
        gemini_result["questions"] = gemini_result["questions"][:count]
        return gemini_result

    # --- Step 2: Extract keywords for fallback ---
    keywords = extract_keywords(code, language)
    if not keywords:
        keywords = [language, "functions", "loops", "variables"]

    # --- Step 3: Build prompt for TinyLLaMA ---
    prompt = (
        f"Generate exactly {count} MCQ viva questions for {language} code.\n"
        f"Concepts: {', '.join(keywords)}.\n"
        "Each question must have 4 options (A,B,C,D) and specify the correct answer.\n"
        "Return only JSON like this format:\n"
        """{
  "marks": X,
  "questions": [
    {
      "question": "Question text",
      "options": ["Option A","Option B","Option C","Option D"],
      "answer": "Correct option text"
    }
  ]
}"""
    )

    result = generate_with_tinyllama(prompt)

    # --- Step 4: Try parsing TinyLLaMA JSON output ---
    mcq_questions = []
    marks = count  # default marks
    if isinstance(result, dict):
        mcq_questions = result.get("questions", [])
        marks = result.get("marks", count)
    elif isinstance(result, str):
        try:
            import json
            parsed = json.loads(result)
            mcq_questions = parsed.get("questions", [])
            marks = parsed.get("marks", count)
        except Exception:
            pass

    # --- Step 5: Fallback templates if TinyLLaMA fails ---
    if not mcq_questions or len(mcq_questions) < count:
        base_templates = [
    (
        "What does {kw} represent in {language}?",
        ["A variable", "A function", "A class", "A loop construct"],
        "A variable"
    ),
    (
        "How is {kw} used in {language}?",
        ["To store values", "To define a function", "To create objects", "To control loops"],
        "To store values"
    ),
    (
        "Why is {kw} important in {language}?",
        ["It stores data", "It allows reusable logic", "It controls program flow", "It handles errors"],
        "It allows reusable logic"
    ),
    (
        "Give an example of {kw} in {language}.",
        ["{kw} = 10", "for {kw} in range(5): pass", "function {kw}() {{}}", "class {kw} {{}}"],
        "{kw} = 10"
    ),
    (
        "What are common mistakes with {kw}?",
        ["Using it before declaration", "Using it correctly", "Ignoring syntax rules", "Not using it at all"],
        "Using it before declaration"
    )
]


        for kw in keywords:
            for question_text, options, answer in base_templates:
                if len(mcq_questions) >= count:
                    break
                mcq_questions.append({
                    "question": question_text.format(kw=kw, language=language),
                    "options": options,
                    "answer": answer
                })

    # --- Step 6: Ensure exactly 'count' questions ---
    mcq_questions = mcq_questions[:count]

    return {
        "marks": marks,
        "questions": mcq_questions
    }
