from pyjsparser import PyJsParser
import itertools

def analyze_javascript(code: str):
    parser = PyJsParser()
    nodes, edges = [], []
    node_counter = itertools.count(1)
    functions = []
    classes = []
    report = []

    def add_node(label, ntype="statement", line=-1):
        node_id = f"n{next(node_counter)}"
        nodes.append({
            "id": node_id,
            "type": ntype,
            "label": label,
            "line": line
        })
        return node_id

    def process_block(statements, parent_id):
        prev_id = parent_id
        for stmt in statements:
            stype = stmt.get("type", "Statement")
            line = stmt.get("loc", {}).get("start", {}).get("line", -1)

            if stype == "IfStatement":
                cond_label = get_expr_label(stmt.get("test", {}))
                if_id = add_node(f"🔀 If ({cond_label})", "decision", line)
                edges.append({"from": prev_id, "to": if_id})

                cons_body = stmt.get("consequent", {}).get("body", []) \
                            if stmt.get("consequent", {}).get("type") == "BlockStatement" else [stmt.get("consequent")] if stmt.get("consequent") else []
                prev_true = if_id
                for cstmt in cons_body:
                    prev_true = process_block([cstmt], prev_true)

                alt = stmt.get("alternate", {})
                if alt:
                    alt_body = alt.get("body", []) if alt.get("type") == "BlockStatement" else [alt]
                    prev_false = if_id
                    for astmt in alt_body:
                        prev_false = process_block([astmt], prev_false)
                    merge_id = add_node("Merge", "merge")
                    edges.append({"from": prev_true, "to": merge_id})
                    edges.append({"from": prev_false, "to": merge_id})
                    prev_id = merge_id
                else:
                    prev_id = prev_true
                report.append(f"\n🔹 If Condition: {cond_label}, Lines: {line}")

            elif stype in ["ForStatement", "WhileStatement", "DoWhileStatement", "ForInStatement", "ForOfStatement"]:
                loop_id = add_node(f"🔁 {stype.replace('Statement', ' Loop')}", "loop", line)
                edges.append({"from": prev_id, "to": loop_id})
                body = stmt.get("body", {})
                loop_body = body.get("body", []) if body.get("type") == "BlockStatement" else [body]
                last_in_loop = loop_id
                for lb_stmt in loop_body:
                    last_in_loop = process_block([lb_stmt], last_in_loop)
                edges.append({"from": last_in_loop, "to": loop_id, "condition": "iterates"})
                prev_id = loop_id
                report.append(f"\n🔹 Loop: {stype}, Lines: {line}")

            elif stype == "ClassDeclaration":
                cname = stmt.get("id", {}).get("name", "AnonymousClass")
                classes.append(cname)
                class_id = add_node(f"📦 Class: {cname}", "class", line)
                edges.append({"from": prev_id, "to": class_id})
                body = stmt.get("body", {}).get("body", [])
                prev_id = process_block(body, class_id)
                report.append(f"\n============================\nClass: {cname}\n============================\n")

            elif stype == "FunctionDeclaration":
                fname = stmt.get("id", {}).get("name", "anonymous")
                functions.append(fname)
                fid = add_node(f"🔧 Function: {fname}", "method", line)
                edges.append({"from": prev_id, "to": fid})
                func_body = stmt.get("body", {}).get("body", [])
                prev_id = process_block(func_body, fid)
                report.append(f"\n🔹 Function: {fname}, Parameters: {len(stmt.get('params', []))}, Lines: {line}")

            else:
                stmt_id = add_node(f"🔸 {stype}", "statement", line)
                edges.append({"from": prev_id, "to": stmt_id})
                prev_id = stmt_id

        return prev_id

    def get_expr_label(expr):
        etype = expr.get("type")
        if etype == "Identifier":
            return expr.get("name", "var")
        if etype == "Literal":
            return str(expr.get("value"))
        if etype == "BinaryExpression":
            return f"{get_expr_label(expr.get('left', {}))} {expr.get('operator', '?')} {get_expr_label(expr.get('right', {}))}"
        if etype == "CallExpression":
            callee = get_expr_label(expr.get("callee", {}))
            args = [get_expr_label(a) for a in expr.get("arguments", [])]
            return f"{callee}({', '.join(args)})"
        if etype == "MemberExpression":
            obj = get_expr_label(expr.get("object", {}))
            prop = get_expr_label(expr.get("property", {}))
            return f"{obj}.{prop}"
        return etype or "expr"

    try:
        parsed = parser.parse(code)
        body = parsed.get("body", [])
        root_id = add_node("Program", "root")
        process_block(body, root_id)

        # ---- Metrics ----
        loc = len([line for line in code.splitlines() if line.strip()])
        complexity = sum(1 for n in nodes if n["type"] in ["decision", "loop"])
        comment_count = len([line for line in code.splitlines() if line.strip().startswith("//")])
        quality_score = max(30, min(100, 100 - complexity * 2))

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
            "language": "javascript",
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

    except Exception as e:
        return {
            "language": "javascript",
            "error": "Parse Error",
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
