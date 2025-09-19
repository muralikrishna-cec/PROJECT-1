import requests
import os
import re
import json

# ✅ Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ✅ TinyLLaMA local fallback
TINYLAMA_API = "http://localhost:5000/chat"


def generate_with_gemini(language: str, code: str, count: int = 5):
    """
    Call Gemini API to generate structured MCQ viva questions.
    Uses only code + language.
    """
    prompt = f"""
    You are an expert PG-level examiner. 
    Generate {count} advanced MCQ viva-style questions for {language} programming.

    🔹 Base the questions on:
    - The programming language: {language}
    - The actual code (syntax and logic):
    ```{language}
    {code}
    ```

    ✅ Requirements:
    - Each question must have exactly 4 options (A,B,C,D).
    - Clearly specify the correct answer.
    - Questions should test language syntax, code logic, and conceptual understanding.
    - Return only valid JSON in this format (no extra text, no explanations):

    {{
      "marks": {count},
      "questions": [
        {{
          "question": "What does the for loop represent?",
          "options": ["Infinite loop","Iterates fixed times","Handles exceptions","Declares a function"],
          "answer": "Iterates fixed times"
        }}
      ]
    }}
    """

    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.5,
                    "maxOutputTokens": 800
                }
            },
            timeout=40
        )
        resp.raise_for_status()
        data = resp.json()

        output_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # ✅ Extract JSON block
        match = re.search(r"\{[\s\S]*\}", output_text)
        if not match:
            print("⚠️ No JSON found in Gemini output:", output_text)
            return {"marks": 0, "questions": []}

        json_str = match.group(0)
        json_str = json_str.replace("```json", "").replace("```", "")
        json_str = re.sub(r",\s*([\]}])", r"\1", json_str)

        try:
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError as e:
            print("⚠️ JSON parse failed:", e, "\nRaw JSON:", json_str)
            return {"marks": 0, "questions": []}

    except Exception as e:
        print("⚠️ Try Again:", e)
        return None


def generate_with_tinyllama(language: str, code: str = "", count: int = 5):
    if not code:
        return {"marks": 0, "questions": [], "error": "No code provided"}
    ...

    """
    Fallback: Call TinyLLaMA API running locally.
    Uses only code + language.
    """
    prompt = f"""
    Generate {count} PG-level viva questions for {language} programming.
    Focus on both syntax and the given code.

    Code:
    ```{language}
    {code}
    ```

    Format:
    Marks: {count}
    1. Question (with 4 options and correct answer)
    ...
    """

    try:
        resp = requests.post(TINYLAMA_API, json={"prompt": prompt}, timeout=40)
        resp.raise_for_status()
        data = resp.json()

        output = data.get("output", "")
        marks, questions = 0, []

        # ✅ Extract marks
        match = re.search(r"Marks:\s*(\d+)", output)
        if match:
            marks = int(match.group(1))

        # ✅ Extract questions
        raw_qs = re.findall(r"\d+\.\s*(.+)", output)
        for q in raw_qs[:count]:
            questions.append({"question": q.strip(), "options": [], "answer": ""})

        return {"marks": marks or count, "questions": questions}

    except Exception:
        return {"marks": 0, "questions": []}


def generate_viva_questions(code: str, language: str, count: int = 5):
    """
    Main function: Try Gemini first → fallback TinyLLaMA.
    """
    gemini_result = generate_with_gemini(language, code, count)
    if gemini_result and gemini_result.get("questions"):
        return gemini_result

    return generate_with_tinyllama(language, code, count)
