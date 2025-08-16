from pyjsparser import PyJsParser
import itertools

def analyze_javascript(code: str):
    parser = PyJsParser()
    nodes, edges = [], []
    node_counter = itertools.count(1)
    functions = []

    def add_node(label, ntype="statement"):
        node_id = f"n{next(node_counter)}"
        nodes.append({"id": node_id, "type": ntype, "label": label})
        return node_id

    try:
        parsed = parser.parse(code)
        body = parsed.get('body', [])

        for item in body:
            if item.get('type') == 'FunctionDeclaration':
                fname = item['id']['name']
                functions.append(fname)
                fid = add_node(f"Function: {fname}", "function")

                body_list = item.get('body', {}).get('body', [])
                prev_id = fid

                for idx, stmt in enumerate(body_list):
                    stmt_type = stmt.get('type', 'Statement')
                    node_label = stmt_type

                    # Handle if-else
                    if stmt_type == "IfStatement":
                        cond = stmt.get('test', {}).get('name', 'condition')
                        if_id = add_node(f"If: {cond}", "decision")
                        edges.append({"from": prev_id, "to": if_id})

                        # Consequent
                        consequent = stmt.get('consequent', {}).get('body', [])
                        prev_true = if_id
                        for cidx, cstmt in enumerate(consequent):
                            cid = add_node(cstmt.get('type', 'Statement'), "statement")
                            edges.append({"from": if_id, "to": cid, "condition": "true"})
                            prev_true = cid

                        # Alternate
                        alternate = stmt.get('alternate', {}).get('body', [])
                        prev_false = if_id
                        for aidx, astmt in enumerate(alternate):
                            aid = add_node(astmt.get('type', 'Statement'), "statement")
                            edges.append({"from": if_id, "to": aid, "condition": "false"})
                            prev_false = aid

                        prev_id = if_id

                    # Handle loops
                    elif stmt_type in ["ForStatement", "WhileStatement"]:
                        loop_id = add_node(stmt_type.replace("Statement", " Loop"), "loop")
                        edges.append({"from": prev_id, "to": loop_id})
                        prev_id = loop_id

                    # Other statements
                    else:
                        stmt_id = add_node(node_label, "statement")
                        edges.append({"from": prev_id, "to": stmt_id})
                        prev_id = stmt_id

        # Metrics
        loc = len([line for line in code.splitlines() if line.strip()])
        complexity = sum(1 for n in nodes if n["type"] in ["decision", "loop"])
        quality_score = max(30, 100 - complexity * 2)

        suggestions = []
        if not functions:
            suggestions.append("⚠️ No functions detected. Consider modularizing your code.")
        if complexity > 10:
            suggestions.append("⚠️ High cyclomatic complexity. Consider simplifying logic.")
        if loc > 100:
            suggestions.append("⚠️ File is long. Consider splitting into smaller modules.")
        if not suggestions:
            suggestions.append("✅ Looks good!")

        report_text = f"""============================
🧠 JavaScript Static Analysis Report
============================

📊 Code Metrics:
🔹 Lines of Code (LOC): {loc}
🔹 Number of Functions: {len(functions)}
🔹 Cyclomatic Complexity: {complexity}
🔹 Code Quality Score: {quality_score}%

💡 Code Quality Suggestions:
""" + "\n".join(suggestions)

        return {
            "report": report_text,
            "metrics": {
                "loc": loc,
                "functions": len(functions),
                "cyclomatic_complexity": complexity,
                "quality_score": quality_score
            },
            "nodes": nodes,
            "edges": edges,
            "suggestions": suggestions
        }

    except Exception as e:
        return {
            "error": "Parse Error",
            "details": str(e),
            "nodes": [],
            "edges": [],
            "metrics": {},
            "suggestions": []
        }
