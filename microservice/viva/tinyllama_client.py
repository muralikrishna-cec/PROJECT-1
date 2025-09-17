import requests
import os

# ✅ Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ✅ TinyLLaMA local fallback
TINYLAMA_API = "http://localhost:5000/chat"


def generate_with_gemini(code: str, language: str):
    """
    Call Gemini API to generate 5 MCQ viva questions.
    """
    prompt = f"""
    You are an AI teacher. Analyze the following {language} code and generate 5 MCQ viva-style questions.
    Each question must have exactly 4 options (A, B, C, D) and specify the correct answer.
    Return output as JSON in this exact format:

    {{
      "marks": 5,
      "questions": [
        {{
          "question": "What does the for loop do in this code?",
          "options": ["Runs infinitely", "Sums numbers 0 to 4", "Prints numbers", "Throws an error"],
          "answer": "Sums numbers 0 to 4"
        }},
        ...
      ]
    }}

    Code:
    {code}
    """

    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800
                }
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()

        # Gemini response parsing
        output_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Try to extract JSON safely
        import json, re
        match = re.search(r"\{.*\}", output_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            return parsed

        return {"marks": 0, "questions": []}

    except Exception as e:
        print("⚠️ Gemini API failed:", e)
        return None


def generate_with_tinyllama(prompt: str):
    """
    Fallback: Call TinyLLaMA API running locally.
    """
    try:
        resp = requests.post(TINYLAMA_API, json={"prompt": prompt}, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        output = data.get("output", "")
        marks = 0
        questions = []

        for line in output.splitlines():
            line = line.strip()
            if line.lower().startswith("marks"):
                try:
                    marks = int(line.split(":")[-1].strip())
                except:
                    marks = 0
            elif line and (line[0].isdigit() or line.startswith("Q")):
                questions.append({"question": line.lstrip("Q1234567890.:- ").strip(),
                                  "options": [], "answer": ""})

        return {
            "marks": marks,
            "questions": questions
        }

    except Exception:
        return {"marks": 0, "questions": []}


def generate_viva_questions(code: str, language: str):
    """
    Main function: Try Gemini, fallback to TinyLLaMA.
    """
    # Step 1: Try Gemini
    gemini_result = generate_with_gemini(code, language)
    if gemini_result and gemini_result["questions"]:
        return gemini_result

    # Step 2: Fallback to TinyLLaMA
    prompt = f"Generate viva questions for this {language} code:\n{code}"
    return generate_with_tinyllama(prompt)
