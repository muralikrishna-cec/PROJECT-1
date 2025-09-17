import re
import ast

def extract_keywords(code: str, language: str):
    """Extract keywords/concepts from code for Python, JavaScript, Java, C, and C++."""
    keywords = set()
    language = language.lower()

    if language == "python":
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    keywords.add("function")
                elif isinstance(node, ast.ClassDef):
                    keywords.add("class")
                elif isinstance(node, ast.For):
                    keywords.add("for loop")
                elif isinstance(node, ast.While):
                    keywords.add("while loop")
                elif isinstance(node, ast.If):
                    keywords.add("if condition")
                elif isinstance(node, ast.Try):
                    keywords.add("exception handling")
                elif isinstance(node, ast.Return):
                    keywords.add("return statement")
        except Exception:
            # fallback to regex scan if AST parsing fails
            if "def " in code:
                keywords.add("function")
            if "class " in code:
                keywords.add("class")
            if "for " in code:
                keywords.add("for loop")
            if "while " in code:
                keywords.add("while loop")
            if "if " in code:
                keywords.add("if condition")

    elif language in ["javascript", "java", "c", "cpp", "c++"]:
        patterns = {
            "class": r"\bclass\b",
            "function/method": r"\b(function|def|void|int|float|double|char|public|private|static)\s+\w+\s*\(",
            "for loop": r"\bfor\s*\(",
            "while loop": r"\bwhile\s*\(",
            "if condition": r"\bif\s*\(",
            "switch case": r"\bswitch\s*\(",
            "exception handling": r"\b(try|catch|throw)\b",
            "return statement": r"\breturn\b",
            "do-while loop": r"\bdo\s*\{"
        }
        for kw, pattern in patterns.items():
            if re.search(pattern, code):
                keywords.add(kw)

    return list(keywords) if keywords else ["general programming concepts"]
