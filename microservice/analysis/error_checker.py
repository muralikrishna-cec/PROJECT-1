import ast
import subprocess
import tempfile
import os
import shutil
import re

# ----------------------------
# ✅ Python Error Checker
# ----------------------------
def check_python_errors(code: str):
    syntax_errors, logic_issues = [], []

    # Syntax check with AST
    try:
        ast.parse(code)
    except SyntaxError as e:
        syntax_errors.append(str(e))

    # Run pylint for logic/style
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(code.encode())
        tmp.flush()
        try:
            proc = subprocess.run(
                ["pylint", "--disable=all", "--enable=E,F,W,R,C", tmp.name],
                capture_output=True, text=True, timeout=10
            )
            if proc.stdout.strip():
                logic_issues.extend(clean_pylint_output(proc.stdout))
        except Exception as e:
            logic_issues.append(f"Pylint error: {str(e)}")
        finally:
            os.unlink(tmp.name)

    return syntax_errors, logic_issues


def clean_pylint_output(output: str):
    errors = []
    for line in output.splitlines():
        match = re.search(r"(.+):(\d+):\d+: \w\d+: (.+)", line)
        if match:
            _, lineno, message = match.groups()
            errors.append(f"Line {lineno}: {message}")
    return errors


# ----------------------------
# ✅ JavaScript Error Checker
# ----------------------------

def check_javascript_errors(code: str):
    syntax_errors, logic_issues = [], []
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as tmp:
        tmp.write(code.encode())
        tmp.flush()

        eslint_config = "/home/krishna/Desktop/ai-code-review-assistant/microservice/analysis/eslint.config.cjs"

        if shutil.which("eslint"):  # Use eslint if available
            proc = subprocess.run(
                ["eslint", "--config", eslint_config, "--no-warn-ignored", tmp.name],
                capture_output=True, text=True, timeout=10,
                cwd="/home/krishna/Desktop/ai-code-review-assistant/microservice/analysis"  # force working dir
            )
            if proc.stdout.strip():
                logic_issues.extend(proc.stdout.strip().split("\n"))
            if proc.stderr.strip():
                syntax_errors.append(proc.stderr.strip())
        else:  # fallback to Node syntax check
            proc = subprocess.run(
                ["node", "--check", tmp.name],
                capture_output=True, text=True, timeout=5
            )
            if proc.returncode != 0:
                syntax_errors.append(proc.stderr.strip())

    os.unlink(tmp.name)
    return syntax_errors, logic_issues

# ----------------------------
# ✅ C / C++ Error Checker
# ----------------------------
def check_c_cpp_errors(code: str, language: str):
    syntax_errors, logic_issues = [], []
    suffix = ".c" if language == "c" else ".cpp"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(code.encode())
        tmp.flush()

        # Syntax check with gcc/g++
        cmd = ["gcc", "-fsyntax-only", tmp.name] if language == "c" else ["g++", "-fsyntax-only", tmp.name]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if proc.returncode != 0 and proc.stderr.strip():
            syntax_errors.append(proc.stderr.strip())

        # Run cppcheck if available
        if shutil.which("cppcheck"):
            proc2 = subprocess.run(
                ["cppcheck", "--enable=all", tmp.name],
                capture_output=True, text=True, timeout=10
            )
            if proc2.stderr.strip():
                logic_issues.extend(proc2.stderr.strip().split("\n"))
        else:
            logic_issues.append("ℹ️ Skipped cppcheck (not installed).")

    os.unlink(tmp.name)
    return syntax_errors, logic_issues


# ----------------------------
# ✅ Java Error Checker
# ----------------------------
import os
import re
import subprocess
import tempfile

def check_java_errors(code: str):
    syntax_errors, logic_issues = [], []

    # Extract public class name for filename
    match = re.search(r"public\s+class\s+(\w+)", code)
    class_name = match.group(1) if match else "TempClass"

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, f"{class_name}.java")
        with open(file_path, "w") as f:
            f.write(code)

        # --- Syntax check (javac) ---
        proc = subprocess.run(
            ["javac", "-Xlint:all", file_path],
            capture_output=True, text=True, timeout=10
        )
        if proc.returncode != 0 and proc.stderr.strip():
            for line in proc.stderr.splitlines():
                match = re.search(r"(.+):(\d+): (error|warning): (.+)", line)
                if match:
                    _, lineno, _, message = match.groups()
                    syntax_errors.append(f"Line {lineno}: {message}")
                else:
                    syntax_errors.append(line.strip())

        # --- Logic check (SpotBugs) ---
        spotbugs_home = os.path.expanduser("~/Desktop/ai-code-review-assistant/microservice/analysis/spotbugs-4.8.6")
        spotbugs_bin = os.path.join(spotbugs_home, "bin", "spotbugs")

        class_file = os.path.join(tmpdir, f"{class_name}.class")

        if os.path.exists(spotbugs_bin) and os.path.exists(class_file):
            try:
                proc2 = subprocess.run(
                    [spotbugs_bin, "-textui", class_file],
                    capture_output=True, text=True, timeout=15
                )
                for line in proc2.stdout.splitlines():
                    if line.strip():
                        logic_issues.append(line.strip())
                if proc2.stderr.strip():
                    logic_issues.append(proc2.stderr.strip())
            except Exception as e:
                logic_issues.append(f"SpotBugs error: {str(e)}")
        else:
            logic_issues.append("ℹ️ Skipped SpotBugs (not found).")

    return syntax_errors, logic_issues
