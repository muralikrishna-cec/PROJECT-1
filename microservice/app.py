from flask import Flask, request, jsonify
from flask_cors import CORS 
from analysis.python_analyzer import analyze_python
from analysis.javascript_analyzer import analyze_javascript
from analysis.c_cpp_analyzer import analyze_c_cpp_with_clang
from plagiarism.checker import perform_plagiarism_check  # ✅ You'll create this

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    code = data.get("code", "")
    language = data.get("language", "").lower()

    if not code or not language:
        return jsonify({"error": "Missing code or language"}), 400

    try:
        if language == "python":
            return jsonify({"report": analyze_python(code)})
        elif language == "javascript":
            return jsonify({"report": analyze_javascript(code)})
        elif language in ["c", "cpp", "c++"]:
            return jsonify({"report": analyze_c_cpp_with_clang(code, language)})
        else:
            return jsonify({"error": f"Unsupported language: {language}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ New route for plagiarism
@app.route("/plagiarism", methods=["POST"])
def plagiarism():
    data = request.get_json()
    code1 = data.get("code1", "")
    code2 = data.get("code2", "")
    language = data.get("language", "").lower()

    if not code1 or not code2 or not language:
        return jsonify({"error": "Missing code1/code2/language"}), 400

    try:
        result = perform_plagiarism_check(code1, code2, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=6000, debug=True)
