import ast
import itertools

def analyze_python(code: str):
    try:
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        node_counter = itertools.count(1)
        nodes, edges = [], []   # ✅ FIXED unpacking issue

        # Safe unparser
        def safe_unparse(node):
            try:
                return ast.unparse(node)
            except Exception:
                return str(node)

        def add_node(label, ntype="statement"):
            node_id = f"n{next(node_counter)}"
            nodes.append({"id": node_id, "type": ntype, "label": label})
            return node_id

        def build_flow(node, parent_id=None):
            if isinstance(node, ast.If):
                curr_id = add_node(f"If: {safe_unparse(node.test)}", "if")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})

                # True branch
                prev_true = curr_id
                for stmt in node.body:
                    child_id = build_flow(stmt, prev_true)
                    if child_id:
                        edges.append({"from": curr_id, "to": child_id, "condition": "true"})
                        prev_true = child_id

                # False branch
                prev_false = curr_id
                for stmt in node.orelse:
                    child_id = build_flow(stmt, prev_false)
                    if child_id:
                        edges.append({"from": curr_id, "to": child_id, "condition": "false"})
                        prev_false = child_id

                return curr_id

            elif isinstance(node, ast.For):
                curr_id = add_node(f"For: {safe_unparse(node.target)} in {safe_unparse(node.iter)}", "for")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body:
                    build_flow(stmt, curr_id)
                return curr_id

            elif isinstance(node, ast.While):
                curr_id = add_node(f"While: {safe_unparse(node.test)}", "while")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body:
                    build_flow(stmt, curr_id)
                return curr_id

            elif isinstance(node, ast.Assign):
                curr_id = add_node(f"Assign: {safe_unparse(node)}", "assign")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, ast.Expr):
                curr_id = add_node(f"Expr: {safe_unparse(node)}", "expr")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, ast.Return):
                curr_id = add_node(f"Return: {safe_unparse(node.value)}", "return")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            else:
                curr_id = add_node(type(node).__name__, "other")
                if parent_id:
                    edges.append({"from": parent_id, "to": curr_id})
                return curr_id

        # ---- Cyclomatic Complexity ----
        def compute_complexity(tree):
            complexity = 1
            for n in ast.walk(tree):
                if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp)):
                    complexity += 1
            return complexity

        # Build graph for each function
        for func in functions:
            func_id = add_node(f"Function: {func.name}", "function")
            for stmt in func.body:
                build_flow(stmt, func_id)

        # ---- Metrics ----
        loc = len([line for line in code.splitlines() if line.strip()])
        complexity = compute_complexity(tree)
        quality_score = max(30, 100 - complexity * 2)

        # ---- Suggestions ----
        suggestions = []
        if not functions:
            suggestions.append("⚠️ No functions detected. Consider modularizing your code.")
        if complexity > 10:
            suggestions.append("⚠️ High cyclomatic complexity. Consider simplifying logic.")
        if loc > 100:
            suggestions.append("⚠️ File is long. Consider splitting into smaller modules.")
        if not suggestions:
            suggestions.append("✅ Looks good!")

        # ---- Pretty Report ----
        report_text = f"""============================
🧠 Python Static Analysis Report
============================

📊 Code Metrics:
🔹 Lines of Code (LOC): {loc}
🔹 Cyclomatic Complexity: {complexity}
🔹 Code Quality Score: {quality_score}%

📦 Functions Detected: {len(functions)}

💡 Code Quality Suggestions:
""" + "\n".join(suggestions)

        return {
            "report": report_text.strip(),
            "metrics": {
                "loc": loc,
                "functions": len(functions),
                "cyclomatic_complexity": complexity,
                "quality_score": f"{quality_score}%"
            },
            "nodes": nodes,
            "edges": edges,
            "suggestions": suggestions
        }

    except SyntaxError as e:
        return {"error": "Syntax Error", "details": str(e)}
