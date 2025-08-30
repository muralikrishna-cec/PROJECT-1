import re

def analyze_java(code: str):
    """
    Simple static analysis for Java files.
    """
    lines = code.splitlines()
    loc = len(lines)

    class_count = len(re.findall(r"\bclass\s+\w+", code))
    method_count = len(re.findall(r"\b(public|private|protected)?\s+\w+\s+\w+\s*\([^)]*\)\s*{", code))

    return {
        "loc": loc,
        "classes": class_count,
        "methods": method_count,
        "note": "Basic Java analysis"
    }
