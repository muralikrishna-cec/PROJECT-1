import ast
import itertools

def analyze_python(code: str):
    try:
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        node_counter = itertools.count(1)
        nodes, edges, report = [], [], []

        def safe_unparse(node):
            try:
                return ast.unparse(node)
            except Exception:
                return str(node)

        def add_node(label, ntype="statement", line=-1):
            node_id = f"n{next(node_counter)}"
            nodes.append({"id": node_id, "type": ntype, "label": label, "line": line})
            return node_id

        def build_flow(node, parent_id=None):
            line = getattr(node, 'lineno', -1)

            if isinstance(node, ast.If):
                curr_id = add_node(f"🔀 If: {safe_unparse(node.test)}", "decision", line)
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                report.append(f"\n🔹 If Condition: {safe_unparse(node.test)}, Line: {line}")
                for stmt in node.body:
                    build_flow(stmt, curr_id)
                for stmt in node.orelse:
                    build_flow(stmt, curr_id)
                return curr_id

            elif isinstance(node, (ast.For, ast.While)):
                loop_type = "For" if isinstance(node, ast.For) else "While"
                loop_desc = f"🔁 {loop_type}: {safe_unparse(node.target) if hasattr(node, 'target') else safe_unparse(node.test)}"
                curr_id = add_node(loop_desc, "loop", line)
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body:
                    build_flow(stmt, curr_id)
                report.append(f"\n🔹 Loop: {loop_type}, Line: {line}")
                return curr_id

            elif isinstance(node, ast.FunctionDef):
                func_id = add_node(f"🔧 Function: {node.name}", "method", line)
                if parent_id:
                    edges.append({"from": parent_id, "to": func_id})
                report.append(f"\n🔹 Function: {node.name}, Parameters: {len(node.args.args)}, Line: {line}")
                for stmt in node.body:
                    build_flow(stmt, func_id)
                return func_id

            elif isinstance(node, ast.ClassDef):
                class_id = add_node(f"📦 Class: {node.name}", "class", line)
                if parent_id:
                    edges.append({"from": parent_id, "to": class_id})
                report.append(f"\n============================\nClass: {node.name}\n============================\n")
                for stmt in node.body:
                    build_flow(stmt, class_id)
                return class_id

            else:
                curr_id = add_node(type(node).__name__, "statement", line)
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                return curr_id

        # Build flow for classes and functions
        root_id = add_node("Module", "root")
        for cls in classes:
            build_flow(cls, root_id)
        for func in functions:
            build_flow(func, root_id)

        # --- Metrics ---
        loc = len([line for line in code.splitlines() if line.strip()])
        complexity = 1 + sum(1 for n in ast.walk(tree) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp)))
        comment_count = len([line for line in code.splitlines() if line.strip().startswith("#")])
        quality_score = max(30, min(100, 100 - complexity*2 - (loc//100)*5))

        suggestions = []
        if not functions:
            suggestions.append("⚠️ No functions detected. Consider modularizing your code.")
        if complexity > 10:
            suggestions.append("⚠️ High cyclomatic complexity. Consider simplifying logic.")
        if loc > 100:
            suggestions.append("⚠️ File is long. Consider splitting into smaller modules.")
        if not suggestions:
            suggestions.append("✅ Looks good!")

        return {
            "language": "python",
            "metrics": {
                "loc": loc,
                "classes": len(classes),
                "methods": len(functions),
                "cyclomatic_complexity": complexity,
                "comments": comment_count,
                "quality_score": quality_score
            },
            "nodes": nodes,
            "edges": edges,
            "suggestions": suggestions,
            "report": "\n".join(report)
        }

    except SyntaxError as e:
        return {
            "language": "python",
            "error": "Syntax Error",
            "details": str(e),
            "metrics": {
                "loc": 0,
                "classes": 0,
                "methods": 0,
                "cyclomatic_complexity": 0,
                "comments": 0,
                "quality_score": 0
            },
            "nodes": [],
            "edges": [],
            "suggestions": [],
            "report": ""
        }
