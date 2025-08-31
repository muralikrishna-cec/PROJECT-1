import re

def analyze_java(code: str):
    """
    Enhanced Java static analysis.
    Returns structured report with LOC, classes, methods, comments, cyclomatic complexity,
    quality score, issues, and suggestions.
    """

    # --- Lines of Code (non-empty) ---
    lines = code.splitlines()
    loc = len([line for line in lines if line.strip()])

    # --- Classes and methods ---
    class_names = re.findall(r"\bclass\s+(\w+)", code)
    method_matches = re.findall(
        r"\b(public|private|protected)?\s+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*{", code
    )
    method_names = [m[1] for m in method_matches]  # extract method names

    # --- Comments ---
    comment_count = len(re.findall(r"//.*|/\*[\s\S]*?\*/", code))

    # --- Cyclomatic complexity ---
    decision_points = len(re.findall(
        r"\bif\s*\(|\bfor\s*\(|\bwhile\s*\(|\bcase\s+|catch\s*\(|&&|\|\||\?", code
    ))
    cyclomatic_complexity = max(1, decision_points + 1)

    # --- Quality score heuristic ---
    quality_score = max(30, min(100, 100 - (cyclomatic_complexity - 1) * 3 - (loc // 100) * 5))

    # --- Issues / Warnings ---
    issues = []
    if "System.out.println" in code:
        issues.append("Consider using a logger instead of System.out.println.")
    if "== null" in code:
        issues.append("Possible null check, consider Optional to avoid NullPointerException.")
    if loc > 500:
        issues.append("Large file detected, consider splitting into smaller classes.")
    if cyclomatic_complexity > 10:
        issues.append("High cyclomatic complexity, consider simplifying methods.")

    # --- Suggestions ---
    suggestions = issues if issues else ["✅ Looks good!"]

    # --- Structured report ---
    report = {
        "language": "java",
        "metrics": {
            "lines_of_code": loc,
            "classes": len(class_names),
            "methods": len(method_names),
            "functions": len(method_names),  # numeric, for frontend consistency
            "comments": comment_count,
            "cyclomatic_complexity": cyclomatic_complexity,
            "quality_score": quality_score
        },
        "classes": class_names,        # list of class names
        "functions": method_names,     # list of method names
        "issues": issues,
        "suggestions": suggestions,
        "note": "Java static analysis completed"
    }

    return report
