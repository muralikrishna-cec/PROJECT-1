package com.codereview.backend.service;

import org.springframework.stereotype.Service;

@Service
public class PlagiarismService {

    public double checkPlagiarism(String code1, String code2) {
        String[] tokens1 = code1.replaceAll("\\s+", "").split("");
        String[] tokens2 = code2.replaceAll("\\s+", "").split("");

        int distance = levenshtein(tokens1, tokens2);
        int maxLen = Math.max(tokens1.length, tokens2.length);

        return (1 - ((double) distance / maxLen)) * 100;
    }

    private int levenshtein(String[] s1, String[] s2) {
        int[][] dp = new int[s1.length + 1][s2.length + 1];

        for (int i = 0; i <= s1.length; i++) {
            for (int j = 0; j <= s2.length; j++) {
                if (i == 0) dp[i][j] = j;
                else if (j == 0) dp[i][j] = i;
                else if (s1[i - 1].equals(s2[j - 1]))
                    dp[i][j] = dp[i - 1][j - 1];
                else
                    dp[i][j] = 1 + Math.min(
                            dp[i - 1][j - 1],
                            Math.min(dp[i - 1][j], dp[i][j - 1])
                    );
            }
        }

        return dp[s1.length][s2.length];
    }
}
