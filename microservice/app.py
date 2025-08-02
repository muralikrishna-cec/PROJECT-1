from flask import Flask, request, jsonify
from analysis.python_analyzer import analyze_python
from analysis.javascript_analyzer import analyze_javascript
from analysis.c_cpp_analyzer import analyze_c_cpp_with_clang

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(port=6000, debug=True)
