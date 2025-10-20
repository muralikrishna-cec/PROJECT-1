import time
import json # Used for final printing/output

# NOTE: The following imports assume the first file is saved as 'viva_client_module.py'
# and is accessible in the Python path (e.g., in the same directory).
from viva.tinyllama_client import (
    generate_with_gemini, 
    generate_with_tinyllama, 
    generate_fallback_questions
)

# --- Global Configuration ---
last_gemini_call = 0
GEMINI_COOLDOWN = 30   # 30 sec rate limit window
GEMINI_MIN_RESPONSE_DELAY = 10 # Enforce a minimum 10-second wait time for Gemini

# --- Unified Controller Function ---
def generate_viva_questions(language: str, code: str, count: int = 5):
    """
    Attempts to get questions from Gemini. If rate-limited, returns a wait message.
    If Gemini is attempted and fails, it immediately falls back to static questions.
    """
    global last_gemini_call
    now = time.time()
    gemini_resp = None
    
    # 1. Check Rate Limit
    if now - last_gemini_call < GEMINI_COOLDOWN:
        wait_time = int(GEMINI_COOLDOWN - (now - last_gemini_call))
        # RETURN IMMEDIATELY if rate-limited, as requested
        return {"response": f" Rate-limited. Please try again after {wait_time} seconds."}
    
    # If not rate-limited, proceed with the API call (2 & 3)
    
    # 2. Try Gemini with Delay
    start_time = time.time()
    try:
        print("[INFO] Calling Gemini API (rotating keys)...")
        gemini_resp = generate_with_gemini(language, code, count)
    except Exception as e:
        print(f"[ERROR] Unexpected error during Gemini call: {e}")
        pass
    
    # 3. Enforce Minimum Delay
    elapsed_time = time.time() - start_time
    time_to_wait = GEMINI_MIN_RESPONSE_DELAY - elapsed_time
    if time_to_wait > 0:
        print(f"[INFO] Waiting for {time_to_wait:.2f} seconds to meet minimum delay...")
        time.sleep(time_to_wait)
    
    last_gemini_call = time.time() 
    

    # 4. Check for Successful Gemini Response
    if gemini_resp and gemini_resp.get("questions"):
        print("[INFO] Generated with Gemini ✅")
        return gemini_resp

    # 5. Fallback to Static Questions (Only if Gemini failed, not rate-limited)
    # This step is reached ONLY if the API call was made but returned no result.
    print("[INFO] Gemini failed to generate questions. Falling back to static MCQs...")
    fallback_resp = generate_fallback_questions(count)
    
    if fallback_resp and fallback_resp.get("questions"):
        return fallback_resp

    # 6. Final Failure: Return a standard error message
    # This covers the case where the API failed AND the fallback function failed.
    return {"response": " server error. Please try again later."}