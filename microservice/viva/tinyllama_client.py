import requests
import os
import re
import json

# Gemini API keys
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY1", "AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y"),
    os.getenv("GEMINI_API_KEY2", "AIzaSyCGm1uGRJhEfl9cKPGNOSku4Ky1uL2G-fU")
]
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# TinyLLaMA local API
TINYLAMA_API = "http://localhost:5000/chat"


# --- Gemini Request ---
def generate_with_gemini(language: str, code: str, count: int = 5):
    prompt = f"""
    Generate exactly 5 multiple-choice viva questions 
    for {language} programming based on the given code.

    Code:
    ```{language}
    {code}
    ```

    Return STRICT JSON only:
    {{
      "marks": {count},
      "questions": [
        {{
          "question": "Question text",
          "options": ["A","B","C","D"],
          "answer": "Correct option text"
        }}
      ]
    }}
    """

    for api_key in GEMINI_API_KEYS:
        try:
            resp = requests.post(
                f"{GEMINI_API_URL}?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 800,
                        "responseMimeType": "application/json"
                    }
                },
                timeout=40
            )
            resp.raise_for_status()
            data = resp.json()

            # Try structured output
            output_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

            if not output_text.strip():
                continue

            cleaned = output_text.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(cleaned)
            parsed["questions"] = parsed.get("questions", [])[:count]
            parsed["marks"] = count
            return parsed

        except Exception as e:
            print(f"[Gemini Error with key {api_key[:10]}...] {e}")

    return None


# --- TinyLLaMA Fallback ---
def generate_with_tinyllama(language: str, code: str, count: int = 5):
    prompt = f"""
    Generate exactly {count} multiple-choice viva questions 
    for {language} programming based on the given code.

    Code:
    ```{language}
    {code}
    ```

    Respond in strict JSON format ONLY:
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
    except Exception as e:
        print(f"[TinyLLaMA Error] {e}")
        return None
