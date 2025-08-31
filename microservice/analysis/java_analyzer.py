import re

def analyze_java(code: str):
    """
    Enhanced Java static analysis returning metrics, suggestions, and a report.
    """

    # --- Lines of Code (non-empty) ---
    lines = code.splitlines()
    loc = len([line for line in lines if line.strip()])

    # --- Comments ---
    comments = len(re.findall(r"//.*|/\*[\s\S]*?\*/", code))

    # --- Classes ---
    class_matches = re.findall(r"\bclass\s+(\w+)", code)
    num_classes = len(class_matches)

    # --- Methods / Functions ---
    method_matches = re.findall(
        r"\b(public|private|protected)?\s+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{", code
    )
    method_names = [m[1] for m in method_matches]
    num_methods = len(method_names)

    # --- Loops ---
    loops = len(re.findall(r"\bfor\s*\(|\bwhile\s*\(|\bdo\s*\{", code, re.IGNORECASE))

    # --- Returns ---
    returns = len(re.findall(r"\breturn\b", code))

    # --- Assignments and Operators ---
    assignments = len(re.findall(r"(?<![=!<>])=(?!=)", code))
    augmented_ops = len(re.findall(r"\+=|-=|\*=|/=|%=|\+\+|--", code))
    operators = len(re.findall(r"\+|-|\*|/|%|==|!=|<=|>=|<|>|\|\||&&|\^|~", code))
    operators += augmented_ops
    assignments += augmented_ops  # augmented assignments count as assignments

    # --- Function Calls (exclude keywords) ---
    keywords = {"if", "for", "while", "switch", "catch", "return", "do", "else", "new"}
    func_calls = len([f for f in re.findall(r"\b(\w+)\s*\(", code) if f not in keywords])

    # --- Cyclomatic complexity ---
    decision_points = len(re.findall(
        r"\bif\s*\(|\bfor\s*\(|\bwhile\s*\(|\bswitch\s*\(|\bcase\b|catch\s*\(|\?", code
    ))
    cyclomatic_complexity = max(1, decision_points + 1)

    # --- Max Nesting (approximation via curly braces) ---
    max_nesting = 0
    current_level = 0
    for c in code:
        if c == '{':
            current_level += 1
            max_nesting = max(max_nesting, current_level)
        elif c == '}':
            current_level = max(0, current_level - 1)

    # --- Quality score heuristic ---
    quality_score = max(
        30,
        min(
            100,
            100 - (cyclomatic_complexity - 1) * 2 - (loc // 100) * 5
        )
    )

    # --- Suggestions ---
    suggestions = []
    if num_methods == 0:
        suggestions.append("⚠️ No methods detected. Consider adding functions.")
    if cyclomatic_complexity > 10:
        suggestions.append("⚠️ High cyclomatic complexity. Consider simplifying methods.")
    if loops > 5:
        suggestions.append("⚠️ Many loops detected. Consider refactoring.")
    if loc > 100:
        suggestions.append("⚠️ File is long. Consider splitting into smaller modules.")
    if max_nesting > 3:
        suggestions.append("⚠️ Deep nesting detected. Consider flattening logic.")
    if not suggestions:
        suggestions.append("✅ Looks good!")

    metrics = {
        "loc": loc,
        "classes": num_classes,
        "functions": num_methods,
        "loops": loops,
        "returns": returns,
        "assignments": assignments,
        "operators": operators,
        "function_calls": func_calls,
        "cyclomatic_complexity": cyclomatic_complexity,
        "max_nesting": max_nesting,
        "comments": comments,
        "quality_score": quality_score
    }

    # --- Report text ---
    report_text = f"""
=================================
🧠 Java Static Analysis Report
=================================

📊 Code Metrics:
🔹 Lines of Code (LOC): {metrics['loc']}
🔹 Classes: {metrics['classes']}
🔹 Functions: {metrics['functions']}
🔹 Loops: {metrics['loops']}
🔹 Returns: {metrics['returns']}
🔹 Assignments: {metrics['assignments']}
🔹 Operators: {metrics['operators']}
🔹 Function Calls: {metrics['function_calls']}
🔹 Cyclomatic Complexity: {metrics['cyclomatic_complexity']}
🔹 Max Nesting: {metrics['max_nesting']}
🔹 Comments: {metrics['comments']}
🔹 Code Quality Score: {metrics['quality_score']}%

💡 Code Quality Suggestions:
""" + "\n".join(suggestions)

    return {
        "report": report_text.strip(),
        "metrics": metrics,
        "suggestions": suggestions,
        "syntax_errors": []
    }
