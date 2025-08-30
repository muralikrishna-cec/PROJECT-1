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
from analysis.java_analyzer import analyze_java   # ✅ new

def analyze_file(path, language):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if language == "python":
        return analyze_python(code)
    elif language == "javascript":
        return analyze_javascript(code)
    elif language in ["c", "cpp"]:
        return analyze_c_cpp(code, language)
    elif language == "java":  # ✅ Java added
        return analyze_java(code)
    else:
        return {"loc": len(code.splitlines()), "note": "Basic metrics only"}

def process_batch(source_type, source_value):
    """
    source_type = "upload" | "github"
    source_value = file path OR github url
    """

    tmpdir = tempfile.mkdtemp(prefix="batch_")
    try:
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

        files_report = []
        summary = {
            "total_loc": 0,
            "total_files": 0,
            "files_with_errors": 0,
        }
        languages = set()

        for root, _, files in os.walk(tmpdir):
            for fname in files:
                if not is_allowed(fname):
                    continue
                fpath = os.path.join(root, fname)
                language = detect_language(fname)
                try:
                    metrics = analyze_file(fpath, language)
                except Exception as e:
                    metrics = {"error": str(e)}
                    summary["files_with_errors"] += 1

                files_report.append({
                    "path": os.path.relpath(fpath, tmpdir),
                    "language": language,
                    "metrics": metrics,
                })

                summary["total_files"] += 1
                if "loc" in metrics and isinstance(metrics["loc"], int):
                    summary["total_loc"] += metrics["loc"]
                languages.add(language)

        report = {
            "repo": {
                "source": source_type,
                "origin": source_value,
                "files_analyzed": summary["total_files"],
                "languages": sorted(list(languages)),
            },
            "files": files_report,
            "summary": summary,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        return report, 200
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
