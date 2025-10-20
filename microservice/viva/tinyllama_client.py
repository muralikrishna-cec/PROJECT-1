import os
import re
import json
import requests

# --- API Configuration ---
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY1", ""),
    os.getenv("GEMINI_API_KEY2", ""),
]
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key]
TINYLAMA_API = os.getenv("TINYLAMA_API_URL", "http://localhost:5000/chat")


# --- Fallback Questions ---
def generate_fallback_questions(count: int = 5):
    """
    Generates a standard set of language-agnostic programming questions
    if all primary API services fail.
    """
    fallback_data = {
      "marks": 5,
      "questions": [
        {
          "question": "In programming, what is the primary purpose of a variable?",
          "options": ["To store data that can be changed or accessed later", "To execute a specific, pre-defined function", "To stop the program from running", "To add comments to the code for readability"],
          "answer": "To store data that can be changed or accessed later"
        },
        {
          "question": "What is the role of an `if-else` statement?",
          "options": ["To repeat a block of code multiple times", "To define a reusable piece of code", "To make decisions and execute different code based on a condition", "To handle errors and exceptions in the code"],
          "answer": "To make decisions and execute different code based on a condition"
        },
        {
          "question": "Which of the following best describes the purpose of a 'for' or 'while' loop?",
          "options": ["To declare a new variable", "To execute a block of code repeatedly as long as a condition is true", "To import external libraries or modules", "To return a value from a function"],
          "answer": "To execute a block of code repeatedly as long as a condition is true"
        },
        {
          "question": "What is the main advantage of using functions (or methods)?",
          "options": ["They make the code run faster", "They allow for code reuse and better organization", "They are the only way to use variables", "They automatically handle all errors"],
          "answer": "They allow for code reuse and better organization"
        },
        {
          "question": "What is the purpose of adding comments to code?",
          "options": ["To be executed by the computer", "To increase the speed of the program", "To explain the code to human readers and improve maintainability", "To store large amounts of data"],
          "answer": "To explain the code to human readers and improve maintainability"
        }
      ]
    }
    fallback_data["questions"] = fallback_data["questions"][:count]
    fallback_data["marks"] = len(fallback_data["questions"])
    return fallback_data


# --- Gemini API Request with Key Rotation ---
def generate_with_gemini(language: str, code: str, count: int = 5):
    """
    Attempts to generate questions by iterating through available Gemini API keys.
    Returns the parsed JSON result or None if all keys fail.
    """
    if not GEMINI_API_KEYS:
        return None

    prompt = f"""
    You are an examiner conducting a postgraduate-level viva in {language}.
    Generate exactly 5 multiple-choice questions (MCQs).
    - 3 questions about general {language} concepts.
    - 2 questions directly about the provided code snippet.
    Code:
    ```{language}
    {code}
    ```
    Respond in a strict JSON format. Do not include any other text or markdown.
    {{
      "marks": {count},
      "questions": [
        {{"question": "Q?", "options": ["A","B","C","D"], "answer": "Correct option"}}
      ]
    }}
    """

    for api_key in GEMINI_API_KEYS:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}

            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status() 
            data = resp.json()

            text = data["candidates"][0]["content"]["parts"][0].get("text", "")
            if not text.strip():
                continue
            
            cleaned = re.sub(r"```(?:json)?", "", text).strip()
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if not match:
                continue

            parsed = json.loads(match.group(0))
            parsed["questions"] = parsed.get("questions", [])[:count]
            parsed["marks"] = count
            return parsed

        except requests.RequestException:
            continue
        except Exception:
            continue
    return None


# --- TinyLLaMA Fallback ---
def generate_with_tinyllama(language: str, code: str, count: int = 5):
    """
    Attempts to generate questions using the TinyLLaMA API.
    Returns the parsed JSON result or None on failure.
    """
    prompt = f"""
    Generate exactly {count} multiple-choice viva questions 
    for {language} programming based on the given code.
    Code:
    ```{language}
    {code}
    ```
    Respond in strict JSON:
    {{
      "marks": {count},
      "questions": [
        {{
          "question": "Q?",
          "options": ["A","B","C","D"],
          "answer": "Correct"
        }}
      ]
    }}
    """
    try:
        resp = requests.post(TINYLAMA_API, json={"prompt": prompt}, timeout=40)
        resp.raise_for_status()
        data = resp.json()
        output = data.get("output", "")

        match = re.search(r"\{[\s\S]*\}", output)
        if match:
            parsed = json.loads(match.group(0))
            parsed["questions"] = parsed.get("questions", [])[:count]
            parsed["marks"] = count
            return parsed
        return None
    except Exception:
        return None