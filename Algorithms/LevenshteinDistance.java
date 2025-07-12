import java.util.Scanner;

public class LevenshteinDistance {

    public static int compute(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];

        for (int i = 0; i <= s1.length(); i++) dp[i][0] = i;
        for (int j = 0; j <= s2.length(); j++) dp[0][j] = j;

        for (int i = 1; i <= s1.length(); i++) {
            for (int j = 1; j <= s2.length(); j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(
                        Math.min(dp[i - 1][j], dp[i][j - 1]),
                        dp[i - 1][j - 1]
                    );
                }
            }
        }

        return dp[s1.length()][s2.length()];
    }

    public static double getSimilarity(String s1, String s2) {
        int maxLength = Math.max(s1.length(), s2.length());
        if (maxLength == 0) return 1.0;
        return 1.0 - (double) compute(s1, s2) / maxLength;
    }

    public static String readMultilineInput(Scanner sc, String label) {
        System.out.println("Enter " + label + " code (type 'EOF' in a new line to finish):");
        StringBuilder code = new StringBuilder();
        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            if (line.trim().equalsIgnoreCase("EOF")) break;
            code.append(line).append("\n");
        }
        return code.toString();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String code1 = readMultilineInput(sc, "CODE 1");
        String code2 = readMultilineInput(sc, "CODE 2");

        long startTime = System.currentTimeMillis();

        double similarity = getSimilarity(code1, code2) * 100;

        long endTime = System.currentTimeMillis();

        System.out.printf("✅ Levenshtein Similarity: %.2f%%\n", similarity);
        System.out.println("⏱ Execution Time: " + (endTime - startTime) + " ms");

        sc.close();
    }
}


/* 

---

## 📘 Levenshtein Distance – Introduction

**Levenshtein Distance** (a.k.a. Edit Distance) is an algorithm used to measure the **minimum number of single-character edits** (insertions, deletions, or substitutions) required to transform one string into another.

---

### 🔍 Why it's useful in code review:

* Helps in **plagiarism detection** by comparing how similar two code files are.
* Can be used to detect **typos** or structural changes between versions.
* Effective for **string-based comparison** of any programming language.

---

### 📊 Time and Space Complexity:

| Complexity       | Value                                                     |
| ---------------- | --------------------------------------------------------- |
| Time Complexity  | `O(m × n)` where `m` and `n` are lengths of input strings |
| Space Complexity | `O(m × n)` due to 2D DP table                             |

---


********************OUTPUT*******************************

//OP-1

 java LevenshteinDistance
Enter CODE 1 code (type 'EOF' in a new line to finish):
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
EOF

Enter CODE 2 code (type 'EOF' in a new line to finish):
public class Welcome {
    public static void main(String[] args) {
        System.out.println("Welcome!");
    }
}
EOF

✅ Levenshtein Similarity: 89.74%
⏱ Execution Time: 2 ms

//OP -2

 java LevenshteinDistance
Enter CODE 1 code (type 'EOF' in a new line to finish):
public class BubbleSort {
    public static void main(String[] args) {
        int[] arr = {5, 3, 8, 4, 2};
        for (int i = 0; i < arr.length - 1; i++) {
            for (int j = 0; j < arr.length - i - 1; j++) {
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }
        for (int num : arr) {
            System.out.print(num + " ");
        }
    }
}
EOF

Enter CODE 2 code (type 'EOF' in a new line to finish):
public class Sorter {
    public static void main(String[] args) {
        int[] data = {10, 7, 3, 1, 9};
        for (int i = 0; i < data.length - 1; i++) {
            for (int j = 0; j < data.length - i - 1; j++) {
                if (data[j] > data[j + 1]) {
                    int swap = data[j];
                    data[j] = data[j + 1];
                    data[j + 1] = swap;
                }
            }
        }
        for (int val : data) {
            System.out.print(val + " ");
        }
    }
}
EOF
✅ Levenshtein Similarity: 88.03%
⏱ Execution Time: 16 ms


******************************************************************************************

//static checking

public class LevenshteinDistance {

    public static int compute(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];

        // Initialize base cases
        for (int i = 0; i <= s1.length(); i++) dp[i][0] = i;
        for (int j = 0; j <= s2.length(); j++) dp[0][j] = j;

        // Compute the distances
        for (int i = 1; i <= s1.length(); i++) {
            for (int j = 1; j <= s2.length(); j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1]; // no operation needed
                } else {
                    dp[i][j] = 1 + Math.min(
                        Math.min(dp[i - 1][j],    // deletion
                                 dp[i][j - 1]),   // insertion
                                 dp[i - 1][j - 1] // substitution
                    );
                }
            }
        }

        return dp[s1.length()][s2.length()];
    }

    // Similarity percentage
    public static double getSimilarity(String s1, String s2) {
        int maxLength = Math.max(s1.length(), s2.length());
        if (maxLength == 0) return 1.0;
        return 1.0 - (double) compute(s1, s2) / maxLength;
    }

    public static void main(String[] args) {
        String code1 = "int add(int a, int b) { return a + b; }";
        String code2 = "int sum(int x, int y) { return x + y; }";

        double similarity = getSimilarity(code1, code2) * 100;
        System.out.printf("Levenshtein Similarity: %.2f%%\n", similarity);
    }
}



*/
