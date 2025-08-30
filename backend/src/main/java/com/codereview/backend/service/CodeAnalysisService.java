package com.codereview.backend.service;

import com.github.javaparser.*;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class CodeAnalysisService {

    public Map<String, Object> analyze(String code) {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> nodes = new ArrayList<>();
        List<Map<String, String>> edges = new ArrayList<>();
        List<String> suggestions = new ArrayList<>();
        StringBuilder report = new StringBuilder();

        try {
            JavaParser parser = new JavaParser();
            ParseResult<CompilationUnit> parseResult = parser.parse(code);

            if (!parseResult.isSuccessful() || parseResult.getResult().isEmpty()) {
                List<String> errors = new ArrayList<>();
                for (Problem p : parseResult.getProblems()) {
                    errors.add(formatParseProblem(p, code));
                }
                result.put("error", errors);
                return result;
            }

            CompilationUnit cu = parseResult.getResult().get();

            // Metrics calculator
            MetricsCalculator metrics = new MetricsCalculator();
            cu.accept(metrics, null);

            int loc = metrics.getLoc();
            int complexity = metrics.getTotalComplexity();
            int qualityScore = Math.max(30, 100 - complexity * 2);

            result.put("metrics", Map.of(
                    "loc", loc,
                    "cyclomatic_complexity", complexity,
                    "quality_score", qualityScore
            ));

            // Suggestion thresholds
            if (complexity > 10) suggestions.add("⚠️ High cyclomatic complexity. Consider simplifying logic.");
            if (loc > 100) suggestions.add("⚠️ File is long. Consider splitting into smaller modules.");

            // Nodes and edges for D3
            int[] counter = {1};
            for (TypeDeclaration<?> type : cu.getTypes()) {
                if (type instanceof ClassOrInterfaceDeclaration) {
                    processClass((ClassOrInterfaceDeclaration) type, null, nodes, edges, suggestions, counter, report);
                }
            }

            if (suggestions.isEmpty()) suggestions.add("✅ Looks good!");

            result.put("nodes", nodes);
            result.put("edges", edges);
            result.put("suggestions", suggestions);
            result.put("report", report.toString());

        } catch (Exception e) {
            result.put("error", List.of("Exception: " + e.getMessage()));
        }

        return result;
    }

    private void processClass(ClassOrInterfaceDeclaration cls, String parentId,
                              List<Map<String, Object>> nodes, List<Map<String, String>> edges,
                              List<String> suggestions, int[] counter, StringBuilder report) {

        String classId = "Class_" + cls.getNameAsString();
        nodes.add(Map.of(
                "id", classId,
                "type", "class",
                "label", "📦 Class: " + cls.getNameAsString(),
                "line", cls.getBegin().map(p -> p.line).orElse(-1)
        ));
        if (parentId != null) edges.add(Map.of("from", parentId, "to", classId));

        report.append("\n============================\nClass: ").append(cls.getNameAsString()).append("\n============================\n");

        int methodCount = 0;
        for (BodyDeclaration<?> member : cls.getMembers()) {
            if (member instanceof MethodDeclaration) {
                methodCount++;
                MethodDeclaration method = (MethodDeclaration) member;
                String methodId = "Method_" + method.getNameAsString();

                int methodLoc = method.getBody().map(b -> (int) b.toString().lines()
                        .map(String::trim)
                        .filter(line -> !line.isEmpty() && !line.startsWith("//"))
                        .count()).orElse(0);

                int methodComplexity = method.getBody().map(MetricsCalculator::countDecisionPointsStatic).orElse(0) + 1;
                int localVarCount = method.getBody().map(MetricsCalculator::countLocalVariablesStatic).orElse(0);
                int maxNesting = method.getBody().map(MetricsCalculator::maxNestingLevelStatic).orElse(0);

                nodes.add(Map.of(
                        "id", methodId,
                        "type", "method",
                        "label", "🔧 Method: " + method.getNameAsString(),
                        "params", method.getParameters().size(),
                        "returnType", method.getType().toString(),
                        "line", method.getBegin().map(p -> p.line).orElse(-1)
                ));
                edges.add(Map.of("from", classId, "to", methodId));

                // Suggestions
                if (!method.getJavadoc().isPresent())
                    suggestions.add("⚠️ Add JavaDoc to method: " + method.getNameAsString());
                if (method.getParameters().size() > 3)
                    suggestions.add("⚠️ Method " + method.getNameAsString() + " has too many parameters.");
                if (methodComplexity > 10)
                    suggestions.add("⚠️ Method " + method.getNameAsString() + " has high cyclomatic complexity.");
                if (methodLoc > 50)
                    suggestions.add("⚠️ Method " + method.getNameAsString() + " is too long.");
                if (maxNesting > 3)
                    suggestions.add("⚠️ Method " + method.getNameAsString() + " has deep nesting.");

                // Append detailed method info to report
                report.append("\n🔹 Method: ").append(method.getNameAsString())
                        .append("\n   Parameters: ").append(method.getParameters().size())
                        .append("\n   Return Type: ").append(method.getType())
                        .append("\n   LOC: ").append(methodLoc)
                        .append("\n   Cyclomatic Complexity: ").append(methodComplexity)
                        .append("\n   Local Variables: ").append(localVarCount)
                        .append("\n   Max Nesting Level: ").append(maxNesting)
                        .append("\n");

                if (method.getBody().isPresent()) {
                    for (Statement stmt : method.getBody().get().getStatements()) {
                        printD3Flow(stmt, methodId, nodes, edges, counter);
                    }
                }

            } else if (member instanceof ClassOrInterfaceDeclaration) {
                processClass((ClassOrInterfaceDeclaration) member, classId, nodes, edges, suggestions, counter, report);
            }
        }
        report.append("\nTotal Methods: ").append(methodCount).append("\n");
    }

    private void printD3Flow(Statement stmt, String parentId,
                             List<Map<String, Object>> nodes, List<Map<String, String>> edges, int[] counter) {

        String nodeId = parentId + "_N" + counter[0]++;
        String label;
        int line = stmt.getBegin().map(p -> p.line).orElse(-1);

        if (stmt instanceof ForStmt) label = "🔁 For Loop";
        else if (stmt instanceof WhileStmt) label = "🔁 While Loop";
        else if (stmt instanceof DoStmt) label = "🔁 Do-While Loop";
        else if (stmt instanceof ForEachStmt) label = "🔁 Enhanced For Loop";
        else if (stmt instanceof IfStmt) label = "🔀 If Condition";
        else if (stmt instanceof SwitchStmt) label = "🔀 Switch Case";
        else if (stmt instanceof TryStmt) label = "⚠️ Try-Catch Block";
        else if (stmt instanceof ExpressionStmt && stmt.toString().contains("System.out"))
            label = "🖨️ " + stmt.toString().replace("System.out.println", "").trim();
        else label = "🔸 " + stmt.toString().trim();

        nodes.add(Map.of(
                "id", nodeId,
                "type", "stmt",
                "label", label,
                "line", line
        ));
        edges.add(Map.of("from", parentId, "to", nodeId));

        if (stmt instanceof BlockStmt) {
            for (Statement nested : ((BlockStmt) stmt).getStatements())
                printD3Flow(nested, nodeId, nodes, edges, counter);
        } else if (stmt instanceof IfStmt) {
            printD3Flow(((IfStmt) stmt).getThenStmt(), nodeId, nodes, edges, counter);
            ((IfStmt) stmt).getElseStmt().ifPresent(elseStmt -> printD3Flow(elseStmt, nodeId, nodes, edges, counter));
        } else if (stmt instanceof ForStmt) printD3Flow(((ForStmt) stmt).getBody(), nodeId, nodes, edges, counter);
        else if (stmt instanceof WhileStmt) printD3Flow(((WhileStmt) stmt).getBody(), nodeId, nodes, edges, counter);
        else if (stmt instanceof DoStmt) printD3Flow(((DoStmt) stmt).getBody(), nodeId, nodes, edges, counter);
    }

    // Metrics Calculator
    private static class MetricsCalculator extends VoidVisitorAdapter<Void> {
        int loc = 0;
        int totalComplexity = 0;

        @Override public void visit(MethodDeclaration md, Void arg) {
            super.visit(md, arg);
            if (md.getBody().isPresent()) {
                BlockStmt body = md.getBody().get();
                loc += (int) body.toString().lines()
                        .map(String::trim)
                        .filter(line -> !line.isEmpty() && !line.startsWith("//"))
                        .count();
                totalComplexity += countDecisionPoints(body) + 1;
            }
        }

        private int countDecisionPoints(Node node) {
            int count = 0;
            for (Node child : node.getChildNodes()) {
                if (child instanceof IfStmt || child instanceof ForStmt || child instanceof WhileStmt
                        || child instanceof DoStmt || child instanceof ForEachStmt || child instanceof SwitchStmt)
                    count++;
                count += countDecisionPoints(child);
            }
            return count;
        }

        public static int countDecisionPointsStatic(Node node) {
            int count = 0;
            for (Node child : node.getChildNodes()) {
                if (child instanceof IfStmt || child instanceof ForStmt || child instanceof WhileStmt
                        || child instanceof DoStmt || child instanceof ForEachStmt || child instanceof SwitchStmt)
                    count++;
                count += countDecisionPointsStatic(child);
            }
            return count;
        }

        public static int countLocalVariablesStatic(Node node) {
            int count = 0;
            for (Node child : node.getChildNodes()) {
                if (child instanceof VariableDeclarator) count++;
                count += countLocalVariablesStatic(child);
            }
            return count;
        }

        public static int maxNestingLevelStatic(Node node) {
            int max = 0;
            for (Node child : node.getChildNodes()) {
                int childLevel = maxNestingLevelStatic(child);
                max = Math.max(max, childLevel);
            }
            if (node instanceof IfStmt || node instanceof ForStmt || node instanceof WhileStmt
                    || node instanceof DoStmt || node instanceof ForEachStmt || node instanceof SwitchStmt)
                max += 1;
            return max;
        }

        public int getLoc() { return loc; }
        public int getTotalComplexity() { return totalComplexity; }
    }

    private String formatParseProblem(Problem problem, String code) {
        String message = problem.getMessage();
        int line = problem.getLocation()
                .flatMap(loc -> loc.getBegin().getRange().map(r -> r.begin.line))
                .orElse(-1);

        if (message.contains("expected \";\"")) message = "Missing semicolon? " + message;
        else if (message.contains("expected \"}\"")) message = "You may have missed a closing curly brace `}`.";
        else if (message.contains("expected \")\"")) message = "Missing closing bracket `)`?";
        else if (message.contains("Found \"else\"")) message = "Found `else` but maybe missing closing `}` for previous block.";

        return "🔸 Line " + line + ": " + message;
    }
}


