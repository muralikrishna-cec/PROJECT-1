import time
from viva.tinyllama_client import generate_with_tinyllama
from viva.tinyllama_client import generate_with_gemini

# --- Global timestamps for rate limiting ---
last_gemini_call = 0
last_tinyllama_call = 0
GEMINI_COOLDOWN = 30   # 30 sec
TINYLLAMA_COOLDOWN = 10  # 10 sec


# --- Step 1: Gemini ---
def try_gemini(code: str, language: str, count: int):
    global last_gemini_call
    now = time.time()

    # Enforce cooldown
    if now - last_gemini_call < GEMINI_COOLDOWN:
        wait_time = int(GEMINI_COOLDOWN - (now - last_gemini_call))
        return {"response": f"⚠️  Try again after {wait_time} sec."}

    try:
        gemini_result = generate_with_gemini(language, code, count)
        last_gemini_call = time.time()
        if gemini_result and gemini_result.get("questions"):
            return gemini_result
    except Exception as e:
        print(f"[Gemini Error] {e}")
    return None


# --- Step 2: TinyLLaMA ---
def try_tinyllama(code: str, language: str, count: int):
    global last_tinyllama_call
    now = time.time()

    if now - last_tinyllama_call < TINYLLAMA_COOLDOWN:
        wait_time = int(TINYLLAMA_COOLDOWN - (now - last_tinyllama_call))
        return {"response": f"⚠️ Rate limit hit (TinyLLaMA). Try again after {wait_time} sec."}

    try:
        tiny_result = generate_with_tinyllama(language, code, count)
        last_tinyllama_call = time.time()
        if tiny_result and tiny_result.get("questions"):
            return tiny_result
    except Exception as e:
        print(f"[TinyLLaMA Error] {e}")
    return None


# --- Controller Function ---
def generate_viva_questions(code: str, language: str, count: int = 5):
    # Step 1: Gemini
    gemini_resp = try_gemini(code, language, count)
    if gemini_resp:
        return gemini_resp

    # Step 2: TinyLLaMA
    tiny_resp = try_tinyllama(code, language, count)
    if tiny_resp:
        return tiny_resp

    # Step 3: Both unavailable
    return {"response": "❌ Gemini & TinyLLaMA unavailable. Please try again later."}
