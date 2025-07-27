package com.codereview.backend.service;

import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class PlagiarismService {

    // Levenshtein Distance algorithm
    public double checkPlagiarism(String code1, String code2) {
        int distance = calculateLevenshtein(code1, code2);
        int maxLength = Math.max(code1.length(), code2.length());

        return (1 - ((double) distance / maxLength)) * 100; // return as percentage
    }

    // Token-based similarity (Jaccard index)
    public double checkTokenSimilarity(String code1, String code2) {
        Set<String> tokens1 = tokenize(code1);
        Set<String> tokens2 = tokenize(code2);

        Set<String> intersection = new HashSet<>(tokens1);
        intersection.retainAll(tokens2);

        Set<String> union = new HashSet<>(tokens1);
        union.addAll(tokens2);

        return ((double) intersection.size() / union.size()) * 100; // return as percentage
    }

    // Tokenize code by splitting on symbols, whitespace, etc.
    private Set<String> tokenize(String code) {
        return Arrays.stream(code.split("[^a-zA-Z0-9]+"))
                .map(String::toLowerCase)
                .filter(token -> !token.isBlank())
                .collect(Collectors.toSet());
    }

    // Basic Levenshtein distance logic
    private int calculateLevenshtein(String a, String b) {
        int[][] dp = new int[a.length() + 1][b.length() + 1];

        for (int i = 0; i <= a.length(); i++) {
            for (int j = 0; j <= b.length(); j++) {
                if (i == 0)
                    dp[i][j] = j;
                else if (j == 0)
                    dp[i][j] = i;
                else
                    dp[i][j] = Math.min(dp[i - 1][j - 1] + costOfSubstitution(a.charAt(i - 1), b.charAt(j - 1)),
                            Math.min(dp[i - 1][j] + 1,
                                    dp[i][j - 1] + 1));
            }
        }
        return dp[a.length()][b.length()];
    }

    private int costOfSubstitution(char a, char b) {
        return a == b ? 0 : 1;
    }
}
