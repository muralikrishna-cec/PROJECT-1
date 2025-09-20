import os
import tempfile
import shutil
import zipfile
import requests
from datetime import datetime

from utils.file_utils import is_allowed, detect_language
from analysis.python_analyzer import analyze_python
from analysis.javascript_analyzer import analyze_javascript
from analysis.c_cpp_analyzer import analyze_c_cpp
from analysis.java_analyzer import analyze_java
from analysis.error_checker import (
    check_python_errors,
    check_javascript_errors,
    check_c_cpp_errors,
    check_java_errors
)

def analyze_file(path, language):
    """Analyze a single file: metrics + syntax + logic issues."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # Default metrics
    base_result = {
        "metrics": {
            "lines_of_code": len(code.splitlines()),
            "functions": 0,
            "loops": 0,
            "cyclomatic_complexity": 0,
            "methods": 0,
            "comments": 0,
            "quality_score": 0
        },
        "classes": [],
        "functions": [],
        "suggestions": [],
        "syntax_errors": [],
        "logic_issues": []
    }

    try:
        # Run existing analyzer
        if language == "python":
            result = analyze_python(code)
            se, le = check_python_errors(code)
        elif language == "javascript":
            result = analyze_javascript(code)
            se, le = check_javascript_errors(code)
        elif language in ["c", "cpp"]:
            result = analyze_c_cpp(code, language)
            se, le = check_c_cpp_errors(code, language)
        elif language == "java":
            result = analyze_java(code)
            se, le = check_java_errors(code)
        else:
            result, se, le = base_result, [], []

        # Merge results with error checks
        result.setdefault("syntax_errors", []).extend(se)
        result.setdefault("logic_issues", []).extend(le)
        return result

    except Exception as e:
        return {**base_result, "syntax_errors": [str(e)]}


def process_batch(source_type, source_value):
    """Process a batch (GitHub repo or uploaded ZIP)."""
    tmpdir = tempfile.mkdtemp(prefix="batch_")
    try:
        # --- 1. Fetch or extract repo ---
        if source_type == "github":
            url = source_value.rstrip("/")
            if url.endswith(".git"):
                url = url[:-4]
            zip_url = url + "/archive/refs/heads/main.zip"
            r = requests.get(zip_url, timeout=20)
            if r.status_code != 200:
                zip_url = url + "/archive/refs/heads/master.zip"
                r = requests.get(zip_url, timeout=20)
            if r.status_code != 200:
                return {"error": "Failed to fetch GitHub repo"}, 400

            zpath = os.path.join(tmpdir, "repo.zip")
            with open(zpath, "wb") as f:
                f.write(r.content)
            with zipfile.ZipFile(zpath, "r") as zf:
                zf.extractall(tmpdir)

        elif source_type == "upload":
            if zipfile.is_zipfile(source_value):
                with zipfile.ZipFile(source_value, "r") as zf:
                    zf.extractall(tmpdir)
            else:
                shutil.copy(source_value, tmpdir)

        # --- 2. Prepare reports ---
        files_report = []
        summary = {
            "total_loc": 0,
            "total_files": 0,
            "files_with_errors": 0,
            "total_cyclomatic_complexity": 0,
            "total_functions": 0,
            "total_loops": 0,
            "syntax_errors_found": 0,
            "logic_issues_found": 0
        }
        languages = set()
        all_suggestions = []

        # Keys to safely accumulate
        numeric_keys = {
            "lines_of_code": "total_loc",
            "cyclomatic_complexity": "total_cyclomatic_complexity",
            "functions": "total_functions",
            "loops": "total_loops"
        }

        # --- 3. Walk repo ---
        for root, _, files in os.walk(tmpdir):
            for fname in files:
                if not is_allowed(fname):
                    continue
                fpath = os.path.join(root, fname)
                language = detect_language(fname)

                try:
                    metrics = analyze_file(fpath, language)
                except Exception as e:
                    metrics = {"metrics": {}, "error": str(e)}
                    summary["files_with_errors"] += 1

                syntax_errs = metrics.get("syntax_errors", [])
                logic_errs = metrics.get("logic_issues", [])

                if syntax_errs or logic_errs:
                    summary["files_with_errors"] += 1
                summary["syntax_errors_found"] += len(syntax_errs)
                summary["logic_issues_found"] += len(logic_errs)

                files_report.append({
                    "path": os.path.relpath(fpath, tmpdir),
                    "language": language,
                    "metrics": metrics.get("metrics", {}),
                    "syntax_errors": syntax_errs,
                    "logic_issues": logic_errs,
                    "suggestions": metrics.get("suggestions", [])
                })

                summary["total_files"] += 1
                languages.add(language)

                # --- 4. Accumulate numeric metrics safely ---
                metrics_data = metrics.get("metrics", {})
                for key, summary_key in numeric_keys.items():
                    value = metrics_data.get(key, 0)
                    if isinstance(value, int):
                        summary[summary_key] += value

                # --- Collect all suggestions ---
                if "suggestions" in metrics and isinstance(metrics["suggestions"], list):
                    all_suggestions.extend(metrics["suggestions"])

        # --- 5. Build final report ---
        report = {
            "repo": {
                "source": source_type,
                "origin": source_value,
                "files_analyzed": summary["total_files"],
                "languages": sorted(list(languages)),
            },
            "files": files_report,
            "summary": summary,
            "suggestions_overall": all_suggestions,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        return report, 200
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
