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
                int returnCount = MetricsCalculator.countReturns(method.getBody().get());
                int loopCount = MetricsCalculator.countLoops(method.getBody().get());
                int conditionalCount = MetricsCalculator.countConditionals(method.getBody().get());
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
                report.append("   Returns: ").append(returnCount)
                        .append(", Loops: ").append(loopCount)
                        .append(", Conditionals: ").append(conditionalCount).append("\n");
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
        int line = stmt.getBegin().map(p -> p.line).orElse(-1);

        // 1️⃣ Clean statement string
        String raw = stmt.toString().replace("\n", " ").replaceAll("\\s+", " ").trim();

        // 2️⃣ Replace long constructs with symbols
        String label = raw;
        label = label.replaceAll("System\\.out\\.println", "🖨️")
                .replaceAll("return", "↩️")
                .replaceAll("if\\s*\\(", "🔀")
                .replaceAll("else", "⬅️")
                .replaceAll("for\\s*\\(", "🔁")
                .replaceAll("while\\s*\\(", "🔁")
                .replaceAll("switch\\s*\\(", "🔀")
                .replaceAll("try\\s*\\{", "⚠️")
                .replaceAll("catch\\s*\\(", "🛑")
                .replaceAll("throw", "✋")
                .replaceAll("synchronized\\s*\\(", "🔒");

        // 3️⃣ Truncate long labels at 50 chars
        int maxLength = 50;
        if (label.length() > maxLength) {
            int spaceIndex = label.lastIndexOf(" ", maxLength);
            label = label.substring(0, spaceIndex > 0 ? spaceIndex : maxLength) + "...";
        }

        // 4️⃣ Determine node type
        String type = "stmt";
        if (stmt instanceof ForStmt || stmt instanceof WhileStmt || stmt instanceof DoStmt || stmt instanceof ForEachStmt) type = "loop";
        else if (stmt instanceof IfStmt || stmt instanceof SwitchStmt) type = "conditional";
        else if (stmt instanceof TryStmt || stmt instanceof SynchronizedStmt) type = "try_catch";
        else if (stmt instanceof ReturnStmt) type = "return";
        else if (stmt instanceof ExpressionStmt && raw.contains("System.out")) type = "print";
        else if (stmt instanceof ExpressionStmt && raw.contains("=")) type = "assignment";
        else if (stmt instanceof ThrowStmt) type = "throw";
        else if (stmt instanceof BreakStmt) type = "break";
        else if (stmt instanceof ContinueStmt) type = "continue";
        else if (stmt instanceof AssertStmt) type = "assert";

        // 5️⃣ Add node and edge
        nodes.add(Map.of(
                "id", nodeId,
                "type", type,
                "label", label,
                "fullStatement", raw,
                "line", line
        ));
        edges.add(Map.of("from", parentId, "to", nodeId));

        // 6️⃣ Logical error checks
        if (stmt instanceof WhileStmt) {
            WhileStmt w = (WhileStmt) stmt;
            if ("true".equals(w.getCondition().toString()) && w.findAll(BreakStmt.class).isEmpty()) {
                nodes.add(Map.of(
                        "id", nodeId + "_err",
                        "type", "error",
                        "label", "⚠️ Potential infinite loop",
                        "line", line
                ));
            }
        } else if (stmt instanceof TryStmt) {
            TryStmt t = (TryStmt) stmt;
            for (CatchClause cc : t.getCatchClauses()) {
                if (cc.getBody().getStatements().isEmpty()) {
                    nodes.add(Map.of(
                            "id", nodeId + "_err",
                            "type", "error",
                            "label", "⚠️ Empty catch block",
                            "line", line
                    ));
                }
            }
        }

        // 7️⃣ Recursively process nested statements
        if (stmt instanceof BlockStmt) {
            for (Statement nested : ((BlockStmt) stmt).getStatements()) {
                printD3Flow(nested, nodeId, nodes, edges, counter);
            }
        } else if (stmt instanceof IfStmt ifStmt) {
            printD3Flow(ifStmt.getThenStmt(), nodeId, nodes, edges, counter);
            ifStmt.getElseStmt().ifPresent(e -> printD3Flow(e, nodeId, nodes, edges, counter));
        } else if (stmt instanceof ForStmt forStmt) printD3Flow(forStmt.getBody(), nodeId, nodes, edges, counter);
        else if (stmt instanceof WhileStmt whileStmt) printD3Flow(whileStmt.getBody(), nodeId, nodes, edges, counter);
        else if (stmt instanceof DoStmt doStmt) printD3Flow(doStmt.getBody(), nodeId, nodes, edges, counter);
        else if (stmt instanceof ForEachStmt forEachStmt) printD3Flow(forEachStmt.getBody(), nodeId, nodes, edges, counter);
        else if (stmt instanceof TryStmt tryStmt) {
            printD3Flow(tryStmt.getTryBlock(), nodeId, nodes, edges, counter);
            for (CatchClause cc : tryStmt.getCatchClauses()) printD3Flow(cc.getBody(), nodeId, nodes, edges, counter);
        } else if (stmt instanceof SynchronizedStmt syncStmt) {
            printD3Flow(syncStmt.getBody(), nodeId, nodes, edges, counter);
        } else if (stmt instanceof LabeledStmt labeledStmt) {
            printD3Flow(labeledStmt.getStatement(), nodeId, nodes, edges, counter);
        }
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

        public static int countReturns(Node node) {
            int count = 0;
            if (node instanceof ReturnStmt) count++;
            for (Node child : node.getChildNodes()) count += countReturns(child);
            return count;
        }

        public static int countLoops(Node node) {
            int count = 0;
            if (node instanceof ForStmt || node instanceof WhileStmt || node instanceof DoStmt || node instanceof ForEachStmt) count++;
            for (Node child : node.getChildNodes()) count += countLoops(child);
            return count;
        }

        public static int countConditionals(Node node) {
            int count = 0;
            if (node instanceof IfStmt || node instanceof SwitchStmt) count++;
            for (Node child : node.getChildNodes()) count += countConditionals(child);
            return count;
        }
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


