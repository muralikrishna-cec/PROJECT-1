from pyjsparser import PyJsParser
import itertools

def analyze_javascript(code: str):
    parser = PyJsParser()
    nodes, edges = [], []
    node_counter = itertools.count(1)
    functions, classes = [], []

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

    def safe_label(label):
        return str(label).replace("\n", " ").strip()

    def add_node(label, ntype="statement", line=-1, full=None):
        node_id = f"n{next(node_counter)}"
        nodes.append({
            "id": node_id,
            "type": ntype,
            "label": safe_label(label),
            "line": line,
            "fullStatement": full or safe_label(label)
        })
        return node_id

    def get_expr_label(expr):
        if not expr:
            return ""
        etype = expr.get("type")
        if etype == "Identifier":
            return expr.get("name", "var")
        if etype == "Literal":
            val = expr.get("value")
            return f'"{val}"' if isinstance(val, str) else str(val)
        if etype in ["BinaryExpression", "LogicalExpression"]:
            left = get_expr_label(expr.get("left"))
            right = get_expr_label(expr.get("right"))
            op = expr.get("operator", "?")
            metrics["operators"] += 1
            return f"{left} {op} {right}"
        if etype == "AssignmentExpression":
            left = get_expr_label(expr.get("left"))
            right = get_expr_label(expr.get("right"))
            op = expr.get("operator", "=")
            metrics["operators"] += 1
            metrics["assignments"] += 1
            return f"{left} {op} {right}"
        if etype == "UpdateExpression":
            arg = get_expr_label(expr.get("argument"))
            metrics["operators"] += 1
            metrics["assignments"] += 1
            prefix = expr.get("prefix", False)
            op = expr.get("operator", "++")
            return f"{op}{arg}" if prefix else f"{arg}{op}"
        if etype == "CallExpression":
            callee = get_expr_label(expr.get("callee"))
            args = [get_expr_label(a) for a in expr.get("arguments", [])]
            metrics["function_calls"] += 1
            return f"{callee}({', '.join(args)})"
        if etype == "MemberExpression":
            obj = get_expr_label(expr.get("object"))
            prop = get_expr_label(expr.get("property"))
            return f"{obj}.{prop}"
        return etype or "expr"

    def process_block(stmts, parent_id, depth=1):
        metrics["max_nesting"] = max(metrics["max_nesting"], depth)
        prev_id = parent_id

        for stmt in stmts:
            if not stmt:
                continue
            stype = stmt.get("type", "Statement")
            line = stmt.get("loc", {}).get("start", {}).get("line", -1)
            curr_id = None

            if stype == "EmptyStatement":
                continue

            # If Statement
            if stype == "IfStatement":
                cond = get_expr_label(stmt.get("test"))
                curr_id = add_node(f"🔀 If ({cond})", "decision", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                metrics["cyclomatic_complexity"] += 1

                cons_body = stmt.get("consequent", {}).get("body", []) \
                    if stmt.get("consequent", {}).get("type") == "BlockStatement" \
                    else [stmt.get("consequent")]
                process_block(cons_body, curr_id, depth+1)

                alt = stmt.get("alternate")
                if alt:
                    alt_body = alt.get("body", []) if alt.get("type") == "BlockStatement" else [alt]
                    process_block(alt_body, curr_id, depth+1)

                prev_id = curr_id

            # Loops
            elif stype in ["ForStatement", "WhileStatement", "DoWhileStatement", "ForInStatement", "ForOfStatement"]:
                loop_label = stype.replace("Statement", " Loop")
                curr_id = add_node(f"🔁 {loop_label}", "loop", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                metrics["loops"] += 1
                metrics["cyclomatic_complexity"] += 1
                body = stmt.get("body", {}).get("body", []) if stmt.get("body", {}).get("type") == "BlockStatement" else [stmt.get("body")]
                process_block(body, curr_id, depth+1)
                prev_id = curr_id

            # Function
            elif stype == "FunctionDeclaration":
                fname = stmt.get("id", {}).get("name", "anonymous")
                functions.append(fname)
                curr_id = add_node(f"🔧 Function: {fname}", "function", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                body = stmt.get("body", {}).get("body", [])
                process_block(body, curr_id, depth+1)
                prev_id = curr_id

            # Class
            elif stype == "ClassDeclaration":
                cname = stmt.get("id", {}).get("name", "AnonymousClass")
                classes.append(cname)
                curr_id = add_node(f"📦 Class: {cname}", "class", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                body = stmt.get("body", {}).get("body", [])
                process_block(body, curr_id, depth+1)
                prev_id = curr_id

            # Return
            elif stype == "ReturnStatement":
                metrics["returns"] += 1
                ret = get_expr_label(stmt.get("argument"))
                curr_id = add_node(f"🔹 Return: {ret}", "return", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                prev_id = curr_id

            # Variable Declaration
            elif stype == "VariableDeclaration":
                for decl in stmt.get("declarations", []):
                    name = decl.get("id", {}).get("name", "var")
                    init = get_expr_label(decl.get("init")) if decl.get("init") else "undefined"
                    metrics["assignments"] += 1
                    curr_id = add_node(f"🔸 Assign: {name} = {init}", "assign", line, full=str(decl))
                    edges.append({"from": prev_id, "to": curr_id})
                    prev_id = curr_id

            # Expression
            elif stype == "ExpressionStatement":
                expr_label = get_expr_label(stmt.get("expression", {}))
                curr_id = add_node(f"🔸 Expr: {expr_label}", "statement", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                prev_id = curr_id

            # Others
            else:
                curr_id = add_node(f"🔸 {stype}", "other", line, full=str(stmt))
                edges.append({"from": prev_id, "to": curr_id})
                prev_id = curr_id

        return prev_id

    try:
        parsed = parser.parse(code)
        root_id = add_node("Program", "root")
        process_block(parsed.get("body", []), root_id)

        # Metrics
        metrics["loc"] = len([l for l in code.splitlines() if l.strip()])
        metrics["comments"] = len([l for l in code.splitlines() if l.strip().startswith("//")])
        metrics["functions"] = len(functions)
        metrics["classes"] = len(classes)
        metrics["cyclomatic_complexity"] += 1
        metrics["quality_score"] = max(30, min(100, 100 - metrics["cyclomatic_complexity"]*2 - (metrics["loc"]//100)*5))

        # Suggestions
        suggestions = []
        if metrics["functions"] == 0: suggestions.append("⚠️ No functions detected.")
        if metrics["cyclomatic_complexity"] > 10: suggestions.append("⚠️ High cyclomatic complexity.")
        if metrics["loc"] > 100: suggestions.append("⚠️ File is long.")
        if metrics["max_nesting"] > 3: suggestions.append("⚠️ Deep nesting.")
        if not suggestions: suggestions.append("✅ Looks good!")

        # Report
        report_text = f"""
=================================
🧠 JavaScript Static Analysis Report
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

    except Exception as e:
        return {
            "report": "",
            "metrics": metrics,
            "nodes": [],
            "edges": [],
            "suggestions": ["❌ Syntax Error"],
            "error": str(e)
        }
