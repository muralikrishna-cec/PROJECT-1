import ast
import subprocess

def check_python_errors(code: str):
    syntax_errors, logic_issues = [], []
    try:
        ast.parse(code)  # Will throw if syntax is invalid
    except SyntaxError as e:
        syntax_errors.append(str(e))

    # Example logic check: unreachable code
    if "return" in code and "print" in code.split("return")[-1]:
        logic_issues.append("Code after return is unreachable.")

    return syntax_errors, logic_issues


def check_javascript_errors(code: str):
    syntax_errors, logic_issues = [], []
    try:
        # Use node --check to validate syntax
        proc = subprocess.run(
            ["node", "--check"],
            input=code.encode("utf-8"),
            capture_output=True,
            timeout=5
        )
        if proc.returncode != 0:
            syntax_errors.append(proc.stderr.decode())
    except Exception as e:
        syntax_errors.append(str(e))

    # Example logic issue: unused variable
    if "var" in code and code.count("var") > 5:
        logic_issues.append("Too many var declarations, consider let/const.")

    return syntax_errors, logic_issues


def check_c_cpp_errors(code: str, language: str):
    syntax_errors, logic_issues = [], []
    try:
        # Write to tmp file, run gcc/clang with -fsyntax-only
        import tempfile, os
        suffix = ".c" if language == "c" else ".cpp"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(code.encode())
            tmp.flush()
            cmd = ["gcc", "-fsyntax-only", tmp.name] if language == "c" else ["g++", "-fsyntax-only", tmp.name]
            proc = subprocess.run(cmd, capture_output=True, timeout=5)
            if proc.returncode != 0:
                syntax_errors.append(proc.stderr.decode())
        os.unlink(tmp.name)
    except Exception as e:
        syntax_errors.append(str(e))

    # Example logic issue: infinite loop
    if "while(1)" in code or "for(;;)" in code:
        logic_issues.append("Possible infinite loop detected.")

    return syntax_errors, logic_issues


def check_java_errors(code: str):
    syntax_errors, logic_issues = [], []
    try:
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".java", delete=False) as tmp:
            tmp.write(code.encode())
            tmp.flush()
            proc = subprocess.run(["javac", tmp.name], capture_output=True, timeout=5)
            if proc.returncode != 0:
                syntax_errors.append(proc.stderr.decode())
        os.unlink(tmp.name)
    except Exception as e:
        syntax_errors.append(str(e))

    # Example logic issue: empty catch blocks
    if "catch" in code and "{}" in code:
        logic_issues.append("Empty catch block found.")

    return syntax_errors, logic_issues
