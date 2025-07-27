from llama_cpp import Llama
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Absolute path to GGUF model
model_path = os.path.join(os.path.dirname(__file__), "tinyllama", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
llm = Llama(model_path=model_path)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    print("📥 Received Prompt:", user_prompt)

    messages = [
        {"role": "system", "content": "You're a Java expert. Answer with clean and commented code."},
        {"role": "user", "content": user_prompt}
    ]

    try:
        output = llm.create_chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )
        response = output['choices'][0]['message']['content'].strip()
        return jsonify({"response": response})
    except Exception as e:
        print("🔥 Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

