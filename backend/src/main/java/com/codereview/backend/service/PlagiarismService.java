package com.codereview.backend.service;

import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class PlagiarismService {

    public Map<String, Object> getPlagiarismReport(String code1, String code2) {
        double levenshteinSim = checkLevenshteinSimilarity(code1, code2);
        TokenResult tokenResult = computeTokenSimilarity(code1, code2);

        String verdict = (levenshteinSim > 80 || tokenResult.tokenSimilarity > 80)
                ? "⚠️ Potential Plagiarism"
                : "✅ Acceptable";

        Map<String, Object> report = new LinkedHashMap<>();
        report.put("levenshteinSimilarity", String.format("%.2f%%", levenshteinSim));
        report.put("tokenSimilarity", String.format("%.2f%%", tokenResult.tokenSimilarity));
        report.put("commonTokensCount", tokenResult.commonTokens.size());
        report.put("totalUniqueTokens", tokenResult.unionTokens.size());
        report.put("commonTokens", tokenResult.commonTokens.stream().limit(10).toList());
        report.put("verdict", verdict);
        return report;
    }

    // Levenshtein Distance percentage
    private double checkLevenshteinSimilarity(String code1, String code2) {
        int distance = calculateLevenshtein(code1, code2);
        int maxLength = Math.max(code1.length(), code2.length());
        return (1 - ((double) distance / maxLength)) * 100;
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

