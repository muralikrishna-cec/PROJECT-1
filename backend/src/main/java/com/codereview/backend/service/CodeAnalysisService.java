package com.codereview.backend.service;

import com.github.javaparser.*;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.springframework.stereotype.Service;

@Service
public class CodeAnalysisService {

    public String analyze(String code) {
        StringBuilder report = new StringBuilder();

        try {
            JavaParser parser = new JavaParser();
            ParseResult<CompilationUnit> result = parser.parse(code);

            if (result.isSuccessful() && result.getResult().isPresent()) {
                CompilationUnit cu = result.getResult().get();

                // Metrics Calculation
                MetricsCalculator metrics = new MetricsCalculator();
                cu.accept(metrics, null);

                int loc = metrics.getLoc();
                int complexity = metrics.getTotalComplexity();
                int codeQualityScore = Math.max(0, 100 - (complexity * 2));

                // Header
                report.append("\n============================\n");
                report.append("🧠 Java Static Analysis Report\n");
                report.append("============================\n\n");

                // Metrics
                report.append("📊 Code Metrics:\n");
                report.append("🔹 Lines of Code (LOC): ").append(loc).append("\n");
                report.append("🔹 Cyclomatic Complexity: ").append(complexity).append("\n");
                report.append("🔹 Code Quality Score: ").append(codeQualityScore).append("%\n");

                // Class & Method Summary
                report.append("\n📦 Class & Method Summary:\n");
                cu.accept(new ClassVisitor(report), null);

                // Loop and Conditions
                report.append("\n🔁 Loop & Condition Summary:\n");
                cu.accept(new LoopConditionVisitor(report), null);

                // Suggestions
                report.append("\n💡 Code Quality Suggestions:\n");
                cu.accept(new SuggestionVisitor(report), null);

                // Mermaid Flow
                report.append("\n🔍 Code Flow Visualization:\n");
                visualizeStructure(cu, report);

                return report.toString();
            } else {
                String[] codeLines = code.split("\\r?\\n");

                for (Problem problem : result.getProblems()) {
                    int line = problem.getLocation()
                            .flatMap(loc -> loc.getBegin().getRange().map(r -> r.begin.line))
                            .orElse(-1);

                    String message = problem.getMessage();

                    if (message.contains("expected \";\"")) {
                        message = "Missing semicolon? " + message;
                    } else if (message.contains("expected \"}\"")) {
                        message = "You may have missed a closing curly brace `}`.";
                    } else if (message.contains("expected \")\"")) {
                        message = "Missing closing bracket `)`?";
                    } else if (message.contains("Found \"else\"")) {
                        message = "Found `else` but maybe missing closing `}` for previous block.";
                    }

                    report.append("🔸 Line ").append(line).append(": ").append(message).append("\n");

                    if (line > 0 && line <= codeLines.length) {
                        report.append("    ➤ Code: ").append(codeLines[line - 1].trim()).append("\n\n");
                    }
                }


                return report.toString();
            }
        } catch (Exception e) {
            return "⚠️ Error analyzing code: " + e.getMessage();
        }
    }

    // ========== Visitors ==========

    private static class ClassVisitor extends VoidVisitorAdapter<Void> {
        StringBuilder report;
        ClassVisitor(StringBuilder report) { this.report = report; }

        @Override public void visit(ClassOrInterfaceDeclaration cd, Void arg) {
            report.append("📦 Class: ").append(cd.getName()).append("\n");
            super.visit(cd, arg);
        }

        @Override public void visit(MethodDeclaration md, Void arg) {
            report.append("  🔧 Method: ").append(md.getName()).append("\n");
            report.append("    📥 Params: ").append(md.getParameters().size())
                    .append(", 🔁 Returns: ").append(md.getType()).append("\n");
            super.visit(md, arg);
        }
    }

    private static class LoopConditionVisitor extends VoidVisitorAdapter<Void> {
        StringBuilder report;
        LoopConditionVisitor(StringBuilder report) { this.report = report; }

        @Override public void visit(ForStmt stmt, Void arg) {
            report.append("🔁 For loop at line: ").append(stmt.getBegin().get().line).append("\n");
            super.visit(stmt, arg);
        }

        @Override public void visit(WhileStmt stmt, Void arg) {
            report.append("🔁 While loop at line: ").append(stmt.getBegin().get().line).append("\n");
            super.visit(stmt, arg);
        }

        @Override public void visit(DoStmt stmt, Void arg) {
            report.append("🔁 Do-While loop at line: ").append(stmt.getBegin().get().line).append("\n");
            super.visit(stmt, arg);
        }

        @Override public void visit(ForEachStmt stmt, Void arg) {
            report.append("🔁 Enhanced For loop at line: ").append(stmt.getBegin().get().line).append("\n");
            super.visit(stmt, arg);
        }

        @Override public void visit(IfStmt stmt, Void arg) {
            report.append("🔀 If statement at line: ").append(stmt.getBegin().get().line).append("\n");
            super.visit(stmt, arg);
        }
    }

    private static class SuggestionVisitor extends VoidVisitorAdapter<Void> {
        StringBuilder report;
        SuggestionVisitor(StringBuilder report) { this.report = report; }

        @Override public void visit(MethodDeclaration md, Void arg) {
            if (!md.getJavadoc().isPresent()) {
                report.append("⚠️  Add JavaDoc to method: ").append(md.getName()).append("\n");
            }
            if (md.getParameters().size() > 3) {
                report.append("⚠️  Method ").append(md.getName()).append(" has too many parameters.\n");
            }
            super.visit(md, arg);
        }

        @Override public void visit(ClassOrInterfaceDeclaration cd, Void arg) {
            if (!cd.getJavadoc().isPresent()) {
                report.append("⚠️  Add JavaDoc to class: ").append(cd.getName()).append("\n");
            }
            super.visit(cd, arg);
        }
    }

    private static class MetricsCalculator extends VoidVisitorAdapter<Void> {
        int loc = 0;
        int totalComplexity = 0;

        @Override public void visit(MethodDeclaration md, Void arg) {
            super.visit(md, arg);

            if (md.getBody().isPresent()) {
                BlockStmt body = md.getBody().get();
                loc += countLines(body);

                for (Statement stmt : body.getStatements()) {
                    totalComplexity += countDecisionPoints(stmt);
                }

                totalComplexity += 1;
            }
        }

        private int countLines(Node node) {
            return (int) node.toString()
                    .lines()
                    .map(String::trim)
                    .filter(line -> !line.isEmpty() && !line.startsWith("//"))
                    .count();
        }

        private int countDecisionPoints(Statement stmt) {
            int[] count = new int[1];

            if (stmt instanceof IfStmt || stmt instanceof ForStmt || stmt instanceof WhileStmt ||
                    stmt instanceof DoStmt || stmt instanceof ForEachStmt) count[0]++;

            if (stmt instanceof BlockStmt) {
                for (Statement s : ((BlockStmt) stmt).getStatements()) {
                    count[0] += countDecisionPoints(s);
                }
            } else if (stmt instanceof IfStmt) {
                count[0] += countDecisionPoints(((IfStmt) stmt).getThenStmt());
                ((IfStmt) stmt).getElseStmt().ifPresent(elseStmt -> count[0] += countDecisionPoints(elseStmt));
            } else if (stmt instanceof ForStmt) {
                count[0] += countDecisionPoints(((ForStmt) stmt).getBody());
            } else if (stmt instanceof WhileStmt) {
                count[0] += countDecisionPoints(((WhileStmt) stmt).getBody());
            } else if (stmt instanceof DoStmt) {
                count[0] += countDecisionPoints(((DoStmt) stmt).getBody());
            }

            return count[0];
        }


        public int getLoc() { return loc; }
        public int getTotalComplexity() { return totalComplexity; }
    }

    // === Mermaid Flow Chart ===

    private static void visualizeStructure(CompilationUnit cu, StringBuilder report) {
        report.append("graph TD\n");
        for (TypeDeclaration<?> type : cu.getTypes()) {
            if (type instanceof ClassOrInterfaceDeclaration) {
                processClass((ClassOrInterfaceDeclaration) type, null, report);
            }
        }
    }

    private static void processClass(ClassOrInterfaceDeclaration cls, String parentId, StringBuilder report) {
        String classId = "Class_" + cls.getNameAsString();
        report.append("  ").append(classId).append("[📦 Class: ").append(cls.getName()).append("]\n");

        if (parentId != null) {
            report.append("  ").append(parentId).append(" --> ").append(classId).append("\n");
        }

        for (BodyDeclaration<?> member : cls.getMembers()) {
            if (member instanceof MethodDeclaration) {
                MethodDeclaration method = (MethodDeclaration) member;
                String methodId = "Method_" + method.getNameAsString().replaceAll("[^a-zA-Z0-9_]", "");
                report.append("  ").append(classId).append(" --> ").append(methodId)
                        .append("[🔧 Method: ").append(method.getName()).append("]\n");

                if (method.getBody().isPresent()) {
                    int[] counter = {1};
                    for (Statement stmt : method.getBody().get().getStatements()) {
                        printMermaidFlow(stmt, methodId, report, counter);
                    }
                }
            } else if (member instanceof ClassOrInterfaceDeclaration) {
                processClass((ClassOrInterfaceDeclaration) member, classId, report);
            }
        }
    }

    private static void printMermaidFlow(Statement stmt, String fromId, StringBuilder report, int[] counter) {
        String nodeId = fromId + "_N" + counter[0]++;

        String label = "";
        if (stmt instanceof ForStmt) label = "🔁 For Loop";
        else if (stmt instanceof WhileStmt) label = "🔁 While Loop";
        else if (stmt instanceof DoStmt) label = "🔁 Do-While Loop";
        else if (stmt instanceof ForEachStmt) label = "🔁 Enhanced For Loop";
        else if (stmt instanceof IfStmt) label = "🔀 If Condition";
        else if (stmt instanceof ExpressionStmt && stmt.toString().contains("System.out")) {
            label = "🖨️ " + stmt.toString().replace("System.out.println", "").trim();
        } else {
            label = "🔸 " + stmt.toString().trim();
        }

        label = label
                .replace("\"", "'")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
                .replace("\n", " ")
                .replace("\r", " ")
                .replaceAll("\\s+", " ")
                .trim();

        report.append("  ").append(fromId).append(" --> ").append(nodeId).append("[\"").append(label).append("\"]\n");

        if (stmt instanceof BlockStmt) {
            for (Statement nested : ((BlockStmt) stmt).getStatements()) {
                printMermaidFlow(nested, nodeId, report, counter);
            }
        } else if (stmt instanceof IfStmt) {
            printMermaidFlow(((IfStmt) stmt).getThenStmt(), nodeId, report, counter);
            ((IfStmt) stmt).getElseStmt().ifPresent(elseStmt -> printMermaidFlow(elseStmt, nodeId, report, counter));
        } else if (stmt instanceof ForStmt) {
            printMermaidFlow(((ForStmt) stmt).getBody(), nodeId, report, counter);
        } else if (stmt instanceof WhileStmt) {
            printMermaidFlow(((WhileStmt) stmt).getBody(), nodeId, report, counter);
        } else if (stmt instanceof DoStmt) {
            printMermaidFlow(((DoStmt) stmt).getBody(), nodeId, report, counter);
        }
    }

}
