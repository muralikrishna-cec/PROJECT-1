import ast
import itertools

def analyze_python(code: str):
    try:
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        node_counter = itertools.count(1)
        nodes, edges = [], []

        # Metrics initialization
        metrics = {
            "loc": 0,
            "classes": 0,
            "functions": 0,
            "loops": 0,
            "returns": 0,
            "assignments": 0,
            "operators": 0,
            "function_calls": 0,
            "cyclomatic_complexity": 0,
            "max_nesting": 0,
            "comments": 0
        }

        def safe_unparse(node):
            try:
                return ast.unparse(node)
            except Exception:
                return str(node)

        def add_node(label, ntype="statement"):
            node_id = f"n{next(node_counter)}"
            nodes.append({"id": node_id, "type": ntype, "label": label})
            return node_id

        def build_flow(node, parent_id=None, depth=1):
            metrics["max_nesting"] = max(metrics["max_nesting"], depth)
            curr_id = None

            if isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
                curr_id = add_node(f"📦 Class: {node.name}", "class")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body: build_flow(stmt, curr_id, depth+1)
                return curr_id

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics["functions"] += 1
                curr_id = add_node(f"🔧 Function: {node.name}", "function")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body: build_flow(stmt, curr_id, depth+1)
                return curr_id

            elif isinstance(node, (ast.For, ast.While)):
                metrics["loops"] += 1
                metrics["cyclomatic_complexity"] += 1
                label = f"🔁 {type(node).__name__}: {safe_unparse(node.target) + ' in ' + safe_unparse(node.iter) if isinstance(node, ast.For) else safe_unparse(node.test)}"
                curr_id = add_node(label, "loop")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body: build_flow(stmt, curr_id, depth+1)
                return curr_id

            elif isinstance(node, ast.If):
                metrics["cyclomatic_complexity"] += 1
                curr_id = add_node(f"🔀 If: {safe_unparse(node.test)}", "decision")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})

                last_true = curr_id
                for stmt in node.body: last_true = build_flow(stmt, last_true, depth+1)

                last_false = curr_id
                for stmt in node.orelse: last_false = build_flow(stmt, last_false, depth+1)

                if node.orelse:
                    merge_id = add_node("Merge", "merge")
                    edges.append({"from": last_true, "to": merge_id})
                    edges.append({"from": last_false, "to": merge_id})
                    return merge_id
                return last_true

            elif isinstance(node, ast.Return):
                metrics["returns"] += 1
                curr_id = add_node(f"🔹 Return: {safe_unparse(node.value)}", "return")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, (ast.Assign, ast.AugAssign)):
                metrics["assignments"] += 1
                if isinstance(node, ast.AugAssign): metrics["operators"] += 1
                curr_id = add_node(f"🔸 Assign: {safe_unparse(node)}", "assign")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, ast.Call):
                metrics["function_calls"] += 1
                curr_id = add_node(f"🖨️ Call: {safe_unparse(node.func)}", "call")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, (ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare)):
                metrics["operators"] += 1
                curr_id = add_node(f"{type(node).__name__}: {safe_unparse(node)}", "expr")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, ast.With):
                curr_id = add_node(f"🔒 With: {', '.join(safe_unparse(item) for item in node.items)}", "with")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body: build_flow(stmt, curr_id, depth+1)
                return curr_id

            elif isinstance(node, ast.Try):
                curr_id = add_node("⚠️ Try", "try_catch")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                for stmt in node.body: build_flow(stmt, curr_id, depth+1)
                for handler in node.handlers:
                    h_id = add_node(f"🛑 Except: {safe_unparse(handler.type)}", "except")
                    edges.append({"from": curr_id, "to": h_id})
                    for stmt in handler.body: build_flow(stmt, h_id, depth+1)
                if node.finalbody:
                    f_id = add_node("🔚 Finally", "finally")
                    edges.append({"from": curr_id, "to": f_id})
                    for stmt in node.finalbody: build_flow(stmt, f_id, depth+1)
                return curr_id

            elif isinstance(node, (ast.Break, ast.Continue, ast.Pass)):
                curr_id = add_node(type(node).__name__, type(node).__name__.lower())
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, ast.Raise):
                curr_id = add_node(f"✋ Raise: {safe_unparse(node.exc)}", "raise")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            elif isinstance(node, ast.Expr):
                curr_id = add_node(safe_unparse(node.value), "expr")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

            else:
                curr_id = add_node(type(node).__name__, "other")
                if parent_id: edges.append({"from": parent_id, "to": curr_id})
                return curr_id

        # Build graph for each function
        for func in functions:
            func_id = add_node(f"Function: {func.name}", "function")
            for stmt in func.body:
                build_flow(stmt, func_id)

        # Metrics calculation
        metrics["loc"] = len([line for line in code.splitlines() if line.strip()])
        metrics["comments"] = len([line for line in code.splitlines() if line.strip().startswith("#")])
        metrics["cyclomatic_complexity"] += 1
        metrics["quality_score"] = max(30, min(100, 100 - metrics["cyclomatic_complexity"]*2 - (metrics["loc"]//100)*5))

        # Suggestions
        suggestions = []
        if metrics["functions"] == 0: suggestions.append("⚠️ No functions detected.")
        if metrics["cyclomatic_complexity"] > 10: suggestions.append("⚠️ High cyclomatic complexity.")
        if metrics["loops"] > 5: suggestions.append("⚠️ Many loops detected.")
        if metrics["loc"] > 100: suggestions.append("⚠️ File is long.")
        if metrics["max_nesting"] > 3: suggestions.append("⚠️ Deep nesting.")
        if not suggestions: suggestions.append("✅ Looks good!")

        # Frontend-ready report
        report_text = f"""
        
=================================
🧠 Python Static Analysis Report
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
            "nodes": nodes,
            "edges": edges,
            "suggestions": suggestions
        }

    except SyntaxError as e:
        return {"error": "Syntax Error", "details": str(e)}
