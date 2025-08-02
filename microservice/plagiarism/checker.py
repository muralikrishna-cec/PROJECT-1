import ast
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any

def levenshtein_similarity(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 0.0

    seq = SequenceMatcher(None, s1, s2)
    return round(seq.ratio() * 100, 2)

def tokenize_code(code: str) -> List[str]:
    # Language-agnostic basic tokenizer (word-based)
    return re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', code)

def jaccard_token_similarity(code1: str, code2: str) -> (float, List[str], int, int):
    tokens1 = set(tokenize_code(code1))
    tokens2 = set(tokenize_code(code2))

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    similarity = round(len(intersection) / len(union) * 100, 2) if union else 0.0
    return similarity, sorted(list(intersection)), len(union), len(intersection)

def ast_similarity_python(code1: str, code2: str) -> float:
    try:
        tree1 = ast.dump(ast.parse(code1))
        tree2 = ast.dump(ast.parse(code2))
        return levenshtein_similarity(tree1, tree2)
    except Exception:
        return 0.0

def perform_plagiarism_check(code1: str, code2: str, language: str) -> Dict[str, Any]:
    language = language.lower()
    levenshtein = levenshtein_similarity(code1, code2)
    token_sim, common_tokens, total_tokens, common_count = jaccard_token_similarity(code1, code2)

    ast_sim = 0.0
    if language == "python":
        ast_sim = ast_similarity_python(code1, code2)

    # Generate verdict
    if levenshtein > 85 and token_sim > 80:
        verdict = "⚠️ Potential Plagiarism"
    elif token_sim > 60:
        verdict = "⚠️ Moderate Similarity"
    else:
        verdict = "✅ No significant plagiarism"

    return {
        "levenshteinSimilarity": f"{levenshtein:.2f}%",
        "tokenSimilarity": f"{token_sim:.2f}%",
        "astSimilarity": f"{ast_sim:.2f}%" if language == "python" else "N/A",
        "commonTokensCount": common_count,
        "totalUniqueTokens": total_tokens,
        "commonTokens": common_tokens,
        "verdict": verdict
    }