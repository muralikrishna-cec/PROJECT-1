import ast
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple


def levenshtein_similarity(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 0.0
    seq = SequenceMatcher(None, s1, s2)
    return round(seq.ratio() * 100, 2)


def tokenize_code(code: str) -> List[str]:
    return re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', code)


def jaccard_token_similarity(code1: str, code2: str) -> Tuple[float, List[str], int, int]:
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


def statement_edit_distance(code1: str, code2: str) -> float:
    stmts1 = [line.strip() for line in code1.splitlines() if line.strip()]
    stmts2 = [line.strip() for line in code2.splitlines() if line.strip()]
    seq = SequenceMatcher(None, stmts1, stmts2)
    return round(seq.ratio() * 100, 2)


def normalize_code_pair(code1: str, code2: str) -> Tuple[str, str, Dict[str, str], Dict[str, str]]:
    """
    Normalize two codes with a shared placeholder mapping to avoid mismatches.
    Returns (norm_code1, norm_code2, placeholder->identifier, identifier->placeholder).
    """
    def clean_code(code):
        code = re.sub(r"#.*", "", code)  # remove comments
        code = re.sub(r'".*?"|\'.*?\'', "STRING", code)  # replace strings
        return code

    code1, code2 = clean_code(code1), clean_code(code2)

    # combined identifiers preserving order of first appearance
    identifiers = []
    for ident in re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code1 + "\n" + code2):
        if ident not in identifiers:
            identifiers.append(ident)

    placeholder_map = {}
    reverse_map = {}
    norm1, norm2 = code1, code2

    for i, ident in enumerate(identifiers, start=1):
        placeholder = f"VAR{i}"
        placeholder_map[placeholder] = ident
        reverse_map[ident] = placeholder
        norm1 = re.sub(rf"\b{ident}\b", placeholder, norm1)
        norm2 = re.sub(rf"\b{ident}\b", placeholder, norm2)

    return norm1, norm2, placeholder_map, reverse_map


def perform_plagiarism_check(code1: str, code2: str, language: str) -> Dict[str, Any]:
    language = language.lower()

    # Normalized comparison (shared)
    norm_code1, norm_code2, placeholder_map, reverse_map = normalize_code_pair(code1, code2)

    levenshtein = levenshtein_similarity(norm_code1, norm_code2)
    token_sim, common_tokens, total_tokens, common_count = jaccard_token_similarity(norm_code1, norm_code2)
    stmt_sim = statement_edit_distance(code1, code2)

    ast_sim = 0.0
    if language == "python":
        ast_sim = ast_similarity_python(code1, code2)

    # Identifier matches: resolve placeholders back to original names
    matches = []
    for tok in common_tokens:
        if tok in placeholder_map:  
            orig = placeholder_map[tok]
            matches.append(f"{orig} → {orig}")
        else:
            matches.append(f"{tok} → {tok}")

    # Weighted final score
    final_score = round((levenshtein * 0.3) + (token_sim * 0.3) + (stmt_sim * 0.2) + (ast_sim * 0.2), 2)

    if final_score > 80:
        verdict = "⚠️ Potential Plagiarism"
    elif final_score > 60:
        verdict = "⚠️ Moderate Similarity"
    else:
        verdict = "✅ No significant plagiarism"

    return {
        "levenshteinSimilarity": f"{levenshtein:.2f}%",
        "tokenSimilarity": f"{token_sim:.2f}%",
        "statementSimilarity": f"{stmt_sim:.2f}%",
        "astSimilarity": f"{ast_sim:.2f}%" if language == "python" else "N/A",
        "commonTokensCount": common_count,
        "totalUniqueTokens": total_tokens,
        "identifierMatches": matches,
        "finalScore": f"{final_score:.2f}%",
        "verdict": verdict
    }
