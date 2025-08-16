import ast
import os
import tempfile
from clang import cindex
import itertools

# Set your libclang path
cindex.Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-14.so.1")

def analyze_c_cpp(code: str, lang: str = "c"):
    nodes, edges = [], []
    node_counter = itertools.count(1)

    def add_node(label, ntype="statement"):
        node_id = f"n{next(node_counter)}"
        nodes.append({"id": node_id, "type": ntype, "label": label})
        return node_id

    # Sanitize labels for D3
    def sanitize(text):
        return (
            text.replace('"', '')
                .replace("'", "")
                .replace(";", "")
                .replace("\\", "")
                .replace("[", "")
                .replace("]", "")
                .replace("\n", "")
                .strip()
        )

    # Temporary file for Clang
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c" if lang == "c" else ".cpp") as f:
        f.write(code.encode())
        file_path = f.name

    index = cindex.Index.create()
    tu = index.parse(file_path)

    def walk(node, parent_id=None, func_prefix=""):
        if node.location and node.location.file and not str(node.location.file).startswith("/tmp"):
            return

        kind = node.kind.name
        label = ""
        ntype = "other"

        if kind == "FUNCTION_DECL":
            label = f"Function: {node.spelling}"
            ntype = "function"
            func_prefix = f"Method_{node.spelling}"
        elif kind == "FOR_STMT":
            label = "For Loop"
            ntype = "for"
        elif kind == "WHILE_STMT":
            label = "While Loop"
            ntype = "while"
        elif kind == "IF_STMT":
            label = "If Statement"
            ntype = "decision"
        elif kind == "RETURN_STMT":
            label = "Return"
            ntype = "return"
        elif kind == "CALL_EXPR":
            label = f"Call: {node.spelling}"
            ntype = "call"
        elif kind == "VAR_DECL":
            label = f"Var: {node.spelling}"
            ntype = "assign"
        elif kind == "BINARY_OPERATOR":
            tokens = " ".join([t.spelling for t in node.get_tokens()])
            label = f"{tokens}"
            ntype = "expr"
        else:
            return  # skip unrecognized nodes

        safe_label = sanitize(label)
        current_id = f"{func_prefix}_N{next(node_counter)}" if func_prefix else f"N{next(node_counter)}"

        nodes.append({"id": current_id, "type": ntype, "label": safe_label})
        if parent_id:
            edges.append({"from": parent_id, "to": current_id})

        for child in node.get_children():
            walk(child, current_id, func_prefix)

    walk(tu.cursor)
    os.unlink(file_path)

    # Metrics
    loc = len([line for line in code.splitlines() if line.strip()])
    complexity = sum(1 for n in nodes if n["type"] in ["decision", "for", "while"])
    quality_score = max(30, 100 - complexity*2)

    suggestions = []
    if complexity > 10:
        suggestions.append("⚠️ High cyclomatic complexity. Consider simplifying logic.")
    if loc > 100:
        suggestions.append("⚠️ File is long. Consider splitting into smaller modules.")
    if not suggestions:
        suggestions.append("✅ Looks good!")

    report_text = f"""============================
🧠 {lang.upper()} Static Analysis Report
============================

📊 Code Metrics:
🔹 Lines of Code (LOC): {loc}
🔹 Cyclomatic Complexity: {complexity}
🔹 Code Quality Score: {quality_score}%

💡 Code Quality Suggestions:
""" + "\n".join(suggestions)

    return {
        "report": report_text,
        "metrics": {
            "loc": loc,
            "cyclomatic_complexity": complexity,
            "quality_score": quality_score
        },
        "nodes": nodes,
        "edges": edges,
        "suggestions": suggestions
    }
