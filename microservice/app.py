from flask import Flask, request, jsonify
from flask_cors import CORS 

# Import analyzers
from analysis.javascript_analyzer import analyze_javascript
from analysis.python_analyzer import analyze_python
from analysis.c_cpp_analyzer import analyze_c_cpp

from plagiarism.checker import perform_plagiarism_check  

from batch.processor import analyze_file,process_batch

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
            report = analyze_python(code)
        elif language == "javascript":
            report = analyze_javascript(code)
        elif language in ["c", "cpp", "c++"]:
            report = analyze_c_cpp(code, language)
        else:
            return jsonify({"error": f"Unsupported language: {language}"}), 400

        return jsonify(report)   # ✅ return consistent JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    

@app.route("/batch", methods=["POST"])
def batch():
    # Accept multipart zip OR JSON with github_url
    try:
        if "file" in request.files:
            f = request.files["file"]
            return jsonify(process_batch("upload", f)), 200
        elif request.is_json:
            body = request.get_json()
            if "github_url" in body:
                report, status = process_batch("github", body["github_url"])
                return jsonify(report), status
        return jsonify({"error": "Provide zip file or github_url"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500       


if __name__ == "__main__":
    app.run(port=6000, debug=True)
