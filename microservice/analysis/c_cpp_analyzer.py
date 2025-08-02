from flask import Flask, request, jsonify
import ast
import os
import tempfile
from pyjsparser import PyJsParser
from clang import cindex

# Point to your libclang shared object
cindex.Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-14.so.1")

# ---------------- C/C++ ----------------

def analyze_c_cpp_with_clang(code, lang):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c" if lang == "c" else ".cpp") as f:
        f.write(code.encode())
        file_path = f.name

    index = cindex.Index.create()
    tu = index.parse(file_path)

    flow_lines = ["graph TD"]
    node_counter = 1

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

    def walk(node, parent_id=None, func_prefix=""):
        nonlocal node_counter

        if node.location and node.location.file and not str(node.location.file).startswith("/tmp"):
            return

        kind = node.kind.name
        label = ""

        if kind == "TRANSLATION_UNIT":
            label = f"📦 File: {os.path.basename(file_path)}"
            func_prefix = "TU"
        elif kind == "FUNCTION_DECL":
            label = f"🔧 Method: {node.spelling}"
            func_prefix = f"Method_{node.spelling}"
        elif kind == "FOR_STMT":
            label = "🔁 For Loop"
        elif kind == "WHILE_STMT":
            label = "🔁 While Loop"
        elif kind == "IF_STMT":
            label = "🔀 If Statement"
        elif kind == "RETURN_STMT":
            label = "🔚 Return"
        elif kind == "CALL_EXPR":
            label = f"🖨️ Call: {node.spelling}"
        elif kind == "BINARY_OPERATOR":
            tokens = " ".join([t.spelling for t in node.get_tokens()])
            label = f"🔸 {tokens}"
        elif kind == "VAR_DECL":
            label = f"🔸 var {node.spelling}"
        elif kind == "DECL_STMT":
            label = "🔸 Declaration"
        elif kind == "COMPOUND_STMT":
            label = "🧱 Compound Block"
        elif kind == "INTEGER_LITERAL":
            tokens = list(node.get_tokens())
            label = f"{tokens[0].spelling}" if tokens else "int"
        elif kind == "DECL_REF_EXPR":
            return  # Skip to reduce clutter
        else:
            return  # Skip unrecognized nodes

        safe_label = sanitize(label)
        current_id = f"{func_prefix}_N{node_counter}"
        node_counter += 1

        flow_lines.append(f'{current_id}["{safe_label}"]')
        if parent_id:
            flow_lines.append(f"{parent_id} --> {current_id}")

        for child in node.get_children():
            walk(child, current_id, func_prefix)

    walk(tu.cursor)
    os.unlink(file_path)

    if len(flow_lines) <= 1:
        flow_lines.append('Node_0["⚠️ No visualizable AST nodes found"]')

    flow_graph = "\n".join(flow_lines)

    report = "\n".join([
        "============================",
        f"🧠 {lang.upper()} Static Analysis Report (Clang)",
        "============================",
        "",
        "📊 Code Metrics:",
        f"🔹 Lines of Code (LOC): {len(code.splitlines())}",
        "🔹 Cyclomatic Complexity: (N/A - AST Only)",
        "🔹 Code Quality Score: (N/A)",
        "",
        "📦 Class & Method Summary:",
        "🔧 Functions extracted from Clang AST",
        "",
        "💡 Code Quality Suggestions:",
        "🧠 Now with structured Mermaid-safe flowchart output.",
        "",
        "🔍 Code Flow Visualization:",
        flow_graph
    ])
    return report
