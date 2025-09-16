# viva_service.py
from viva.keyword_extractor import extract_keywords
from viva.tinyllama_client import generate_with_tinyllama
import random

def generate_viva_questions(code: str, language: str, count: int = 10):
    """
    Generate viva questions + marks for given code and language.
    Uses keyword extraction + TinyLLaMA for question generation.
    """
    keywords = extract_keywords(code, language)

    prompt = (
        f"Generate exactly {count} viva questions for {language} code.\n"
        f"Concepts: {', '.join(keywords)}.\n"
        "Do NOT include answers.\n"
        "Start with: 'Marks: X' (where X is out of 10).\n"
        "Then list the questions, one per line, numbered 1 to {count}."
    )

    # --- Call TinyLLaMA ---
    result = generate_with_tinyllama(prompt)

    marks = result.get("marks", 0)
    questions = result.get("questions", [])

    # --- Fallback if TinyLLaMA fails ---
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

        generic = [
            f"What are key features of {language}?",
            f"Explain error handling in {language}.",
            f"How does memory management work in {language}?",
            f"What is the difference between compilation and interpretation in {language}?",
            f"How do loops work in {language}?",
            f"Explain functions in {language}.",
            f"How does input/output work in {language}?"
        ]
        while len(questions) < count:
            questions.append(random.choice(generic))

    # --- Deduplicate & Trim ---
    questions = list(dict.fromkeys(questions))[:count]

    # --- Marks fallback ---
    if marks == 0:
        marks = random.randint(5, 9)

    return {
        "marks": marks,
        "questions": questions
    }
