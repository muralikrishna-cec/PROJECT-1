package com.codereview.backend.service;

import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class PlagiarismService {

    public Map<String, Object> getPlagiarismReport(String code1, String code2) {
        // Metrics
        double levenshteinSim = checkLevenshteinSimilarity(code1, code2);
        TokenResult tokenResult = computeTokenSimilarity(code1, code2);
        double statementSim = checkStatementSimilarity(code1, code2);

        // Stub for now (only Python microservice computes AST properly)
        String astSim = "N/A";

        // Identifier matches (simple: common tokens mapped as a → a)
        List<String> identifierMatches = tokenResult.commonTokens.stream()
                .map(tok -> tok + " → " + tok)
                .sorted()
                .toList();

        // Weighted final score
        double finalScore = (levenshteinSim * 0.3)
                + (tokenResult.tokenSimilarity * 0.3)
                + (statementSim * 0.2)
                + (astSim.equals("N/A") ? 0.0 : Double.parseDouble(astSim.replace("%", "")) * 0.2);

        String verdict;
        if (finalScore > 80) {
            verdict = "⚠️ Potential Plagiarism";
        } else if (finalScore > 60) {
            verdict = "⚠️ Moderate Similarity";
        } else {
            verdict = "✅ No significant plagiarism";
        }

        // Build report
        Map<String, Object> report = new LinkedHashMap<>();
        report.put("levenshteinSimilarity", String.format("%.2f%%", levenshteinSim));
        report.put("tokenSimilarity", String.format("%.2f%%", tokenResult.tokenSimilarity));
        report.put("statementSimilarity", String.format("%.2f%%", statementSim));
        report.put("astSimilarity", astSim);
        report.put("commonTokensCount", tokenResult.commonTokens.size());
        report.put("totalUniqueTokens", tokenResult.unionTokens.size());
        report.put("identifierMatches", identifierMatches);
        report.put("finalScore", String.format("%.2f%%", finalScore));
        report.put("verdict", verdict);
        return report;
    }

    // Levenshtein Distance percentage
    private double checkLevenshteinSimilarity(String code1, String code2) {
        int distance = calculateLevenshtein(code1, code2);
        int maxLength = Math.max(code1.length(), code2.length());
        return maxLength == 0 ? 0.0 : (1 - ((double) distance / maxLength)) * 100;
    }

    // Token structure
    private record TokenResult(double tokenSimilarity, Set<String> commonTokens, Set<String> unionTokens) {}

    private TokenResult computeTokenSimilarity(String code1, String code2) {
        Set<String> tokens1 = tokenize(code1);
        Set<String> tokens2 = tokenize(code2);

        Set<String> common = new HashSet<>(tokens1);
        common.retainAll(tokens2);

        Set<String> union = new HashSet<>(tokens1);
        union.addAll(tokens2);

        double similarity = union.isEmpty() ? 0.0 : ((double) common.size() / union.size()) * 100;
        return new TokenResult(similarity, common, union);
    }

    private Set<String> tokenize(String code) {
        return Arrays.stream(code.split("[^a-zA-Z0-9]+"))
                .map(String::toLowerCase)
                .filter(token -> !token.isBlank())
                .collect(Collectors.toSet());
    }

    // Statement similarity: line-level comparison
    private double checkStatementSimilarity(String code1, String code2) {
        List<String> stmts1 = Arrays.stream(code1.split("\\R"))
                .map(String::trim).filter(s -> !s.isEmpty()).toList();
        List<String> stmts2 = Arrays.stream(code2.split("\\R"))
                .map(String::trim).filter(s -> !s.isEmpty()).toList();

        int matches = 0;
        for (String stmt : stmts1) {
            if (stmts2.contains(stmt)) matches++;
        }

        int total = Math.max(stmts1.size(), stmts2.size());
        return total == 0 ? 0.0 : ((double) matches / total) * 100;
    }

    private int calculateLevenshtein(String a, String b) {
        int[][] dp = new int[a.length() + 1][b.length() + 1];
        for (int i = 0; i <= a.length(); i++) {
            for (int j = 0; j <= b.length(); j++) {
                if (i == 0)
                    dp[i][j] = j;
                else if (j == 0)
                    dp[i][j] = i;
                else
                    dp[i][j] = Math.min(
                            dp[i - 1][j - 1] + costOfSubstitution(a.charAt(i - 1), b.charAt(j - 1)),
                            Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1)
                    );
            }
        }
        return dp[a.length()][b.length()];
    }

    private int costOfSubstitution(char a, char b) {
        return a == b ? 0 : 1;
    }
}
