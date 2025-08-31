import os
import tempfile
from clang import cindex
import itertools

# Set your libclang path
cindex.Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-14.so.1")

def analyze_c_cpp(code: str, lang: str = "c"):
    nodes, edges = [], []
    node_counter = itertools.count(1)
    metrics = {
        "loc": 0,
        "classes": 0,
        "functions": 0,
        "loops": 0,
        "returns": 0,
        "assignments": 0,
        "operators": 0,
        "cyclomatic_complexity": 0,
        "max_nesting": 0,
        "comments": 0
    }
    report_lines = []

    def sanitize(text):
        return text.replace('"', '').replace("'", "").replace(";", "").replace("\\", "").replace("\n", "").strip()

    def add_node(label, ntype="statement", parent_id=None):
        node_id = f"n{next(node_counter)}"
        nodes.append({"id": node_id, "type": ntype, "label": sanitize(label)})
        if parent_id:
            edges.append({"from": parent_id, "to": node_id})
        return node_id

    # Temporary file for Clang
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c" if lang == "c" else ".cpp") as f:
        f.write(code.encode())
        file_path = f.name

    index = cindex.Index.create()
    tu = index.parse(file_path)

    def walk(node, parent_id=None, depth=0, func_prefix=""):
        metrics["max_nesting"] = max(metrics["max_nesting"], depth)
        kind = node.kind.name
        label = ""
        ntype = None
        current_id = None

        if kind == "FUNCTION_DECL":
            label = f"🔧 Function: {node.spelling}"
            ntype = "function"
            metrics["functions"] += 1
            func_prefix = f"{node.spelling}"
            current_id = add_node(label, ntype, parent_id)
            report_lines.append(f"Function: {node.spelling}")
        elif kind in ["FOR_STMT", "WHILE_STMT", "DO_STMT"]:
            label = f"🔁 {kind.replace('_STMT',' Loop')}"
            ntype = "loop"
            metrics["loops"] += 1
            metrics["cyclomatic_complexity"] += 1
            current_id = add_node(label, ntype, parent_id)
            report_lines.append(f"Loop: {label}")
        elif kind == "IF_STMT":
            label = "🔀 If Statement"
            ntype = "decision"
            metrics["cyclomatic_complexity"] += 1
            current_id = add_node(label, ntype, parent_id)
            report_lines.append(f"If: {label}")
        elif kind == "RETURN_STMT":
            label = "🔹 Return"
            ntype = "return"
            metrics["returns"] += 1
            current_id = add_node(label, ntype, parent_id)
            report_lines.append(f"Return: {label}")
        elif kind == "VAR_DECL":
            label = f"🔸 Var: {node.spelling}"
            ntype = "assign"
            metrics["assignments"] += 1
            current_id = add_node(label, ntype, parent_id)
        elif kind in ["BINARY_OPERATOR", "UNARY_OPERATOR"]:
            tokens = " ".join([t.spelling for t in node.get_tokens()])
            label = f"🔸 {tokens}"
            ntype = "expr"
            metrics["operators"] += sum(1 for t in ["+","-","*","/","%","=","+=","-=","*=","/=","==","!=","<",">","<=",">="] if t in tokens)
            if kind == "UNARY_OPERATOR":
                metrics["assignments"] += 1
            current_id = add_node(label, ntype, parent_id)
        elif kind == "CALL_EXPR":
            label = f"🖨️ Call: {node.spelling}"
            ntype = "call"
            metrics["function_calls"] += 1
            current_id = add_node(label, ntype, parent_id)
        else:
            label = kind
            ntype = "statement"
            current_id = add_node(label, ntype, parent_id)

        for child in node.get_children():
            walk(child, current_id, depth+1, func_prefix)

    walk(tu.cursor)
    os.unlink(file_path)

    # Metrics
    metrics["loc"] = len([l for l in code.splitlines() if l.strip()])
    metrics["comments"] = len([l for l in code.splitlines() if l.strip().startswith("//") or l.strip().startswith("/*")])
    metrics["cyclomatic_complexity"] += 1  # base complexity
    metrics["quality_score"] = max(30, min(100, 100 - metrics["cyclomatic_complexity"]*2 - (metrics["loc"]//100)*5))

    # Suggestions
    suggestions = []
    if metrics["functions"] == 0: suggestions.append("⚠️ No functions detected.")
    if metrics["cyclomatic_complexity"] > 10: suggestions.append("⚠️ High cyclomatic complexity.")
    if metrics["loc"] > 100: suggestions.append("⚠️ File is long.")
    if metrics["max_nesting"] > 3: suggestions.append("⚠️ Deep nesting.")
    if not suggestions: suggestions.append("✅ Looks good!")

    # Report text
    report_text = f"""
=================================
🧠 C/C++ Static Analysis Report
=================================

📊 Code Metrics:
🔹 Lines of Code (LOC): {metrics['loc']}
🔹 Functions: {metrics['functions']}
🔹 Loops: {metrics['loops']}
🔹 Returns: {metrics['returns']}
🔹 Assignments: {metrics['assignments']}
🔹 Operators: {metrics['operators']}
🔹 Cyclomatic Complexity: {metrics['cyclomatic_complexity']}
🔹 Max Nesting: {metrics['max_nesting']}
🔹 Comments: {metrics['comments']}
🔹 Code Quality Score: {metrics['quality_score']}%

💡 Code Quality Suggestions:
""" + "\n".join(suggestions)

    return {
        "report": report_text.strip(),
        "metrics": metrics,
        "nodes": nodes,
        "edges": edges,
        "suggestions": suggestions
    }
