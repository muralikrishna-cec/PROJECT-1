package com.codereview.backend.service;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.stmt.Statement;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CodeAnalysisService {

    public String analyze(String code) {
        try {
            JavaParser parser = new JavaParser();
            CompilationUnit cu = parser.parse(code).getResult().orElse(null);

            if (cu == null) {
                return "Parsing failed: Invalid Java code!";
            }

            long lineCount = code.lines().count();
            long loopCount = cu.findAll(Statement.class).stream()
                    .filter(s -> s.isForStmt() || s.isWhileStmt() || s.isIfStmt())
                    .count();

            return String.format("Lines of Code: %d\nLoop/Condition Count: %d", lineCount, loopCount);
        } catch (Exception e) {
            return "Error during analysis: " + e.getMessage();
        }
    }
}
