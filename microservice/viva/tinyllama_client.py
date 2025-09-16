# tinyllama_client.py
import requests

TINYLAMA_API = "http://localhost:5000/chat"

def generate_with_tinyllama(prompt: str):
    """
    Call TinyLLaMA API running locally and return parsed marks/questions.
    Expected TinyLLaMA response format:
    { "output": "Marks: 8\nQ1. ...\nQ2. ..." }
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
                # Strip leading numbering
                questions.append(line.lstrip("Q1234567890.:- ").strip())

        return {
            "marks": marks,
            "questions": questions
        }

    except Exception:
        # Safe fallback
        return {
            "marks": 0,
            "questions": []
        }
