import java.util.*;

public class TokenBasedSimilarity {

    // Tokenizes code into unique lowercase keywords/identifiers
    public static Set<String> tokenize(String code) {
        // Removes non-alphanumeric characters, splits by space
        String cleaned = code.replaceAll("[^a-zA-Z0-9]", " ");
        String[] tokens = cleaned.toLowerCase().split("\\s+");
        return new HashSet<>(Arrays.asList(tokens));
    }

    // Calculates Jaccard similarity: intersection / union
    public static double getSimilarity(String code1, String code2) {
        Set<String> tokens1 = tokenize(code1);
        Set<String> tokens2 = tokenize(code2);

        Set<String> intersection = new HashSet<>(tokens1);
        intersection.retainAll(tokens2);

        Set<String> union = new HashSet<>(tokens1);
        union.addAll(tokens2);

        if (union.size() == 0) return 1.0;

        return (double) intersection.size() / union.size();
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

        System.out.printf("✅ Token-Based Similarity: %.2f%%\n", similarity);
        System.out.println("⏱ Execution Time: " + (endTime - startTime) + " ms");

        sc.close();
    }
}








/*

******************************OUTPUT************************************
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
    }
}
EOF
Enter CODE 2 code (type 'EOF' in a new line to finish):
public class SelectionSort {
    public static void main(String[] args) {
        int[] arr = {64, 25, 12, 22, 11};
        for (int i = 0; i < arr.length - 1; i++) {
            int min = i;
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[j] < arr[min]) {
                    min = j;
                }
            }
            int temp = arr[min];
            arr[min] = arr[i];
            arr[i] = temp;
        }
    }
}
EOF
✅ Token-Based Similarity: 56.67%
⏱ Execution Time: 4 ms

***********************************************************************
import java.util.*;

public class TokenBasedSimilarity {

    public static Set<String> tokenize(String code) {
        // Very basic tokenizer — feel free to improve with regex
        String cleaned = code.replaceAll("[^a-zA-Z0-9]", " ");
        String[] tokens = cleaned.toLowerCase().split("\\s+");
        return new HashSet<>(Arrays.asList(tokens));
    }

    public static double getSimilarity(String code1, String code2) {
        Set<String> tokens1 = tokenize(code1);
        Set<String> tokens2 = tokenize(code2);

        Set<String> intersection = new HashSet<>(tokens1);
        intersection.retainAll(tokens2);

        Set<String> union = new HashSet<>(tokens1);
        union.addAll(tokens2);

        if (union.size() == 0) return 1.0;

        return (double) intersection.size() / union.size();
    }

    public static void main(String[] args) {
        String code1 = "int add(int a, int b) { return a + b; }";
        String code2 = "int sum(int x, int y) { return x + y; }";

        double similarity = getSimilarity(code1, code2) * 100;
        System.out.printf("Token-Based Similarity: %.2f%%\n", similarity);
    }
}

*/