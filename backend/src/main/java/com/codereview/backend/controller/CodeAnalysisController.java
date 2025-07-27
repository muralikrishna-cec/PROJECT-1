package com.codereview.backend.controller;

import com.codereview.backend.model.AISuggestionRequest;
import com.codereview.backend.service.AISuggestionService;
import com.codereview.backend.service.CodeAnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.codereview.backend.model.PlagiarismRequest;
import com.codereview.backend.service.PlagiarismService;


@CrossOrigin(origins = "http://localhost:4200")
@RestController
@RequestMapping("/api")
public class CodeAnalysisController {

    @Autowired
    private CodeAnalysisService codeAnalysisService;

    @Autowired
    private PlagiarismService plagiarismService;

    @Autowired
    private AISuggestionService aiSuggestionService;

    @PostMapping("/analyze")
    public ResponseEntity<String> analyzeCode(@RequestBody String code) {
        String result = codeAnalysisService.analyze(code);
        return ResponseEntity.ok(result);
    }

    @PostMapping("/plagiarism")
    public ResponseEntity<String> checkPlagiarism(@RequestBody PlagiarismRequest request) {
        double similarity = plagiarismService.checkPlagiarism(request.getCode1(), request.getCode2());
        return ResponseEntity.ok(String.format("Similarity: %.2f%%", similarity));
    }

    @PostMapping("/ai-suggest")
    public ResponseEntity<String> getAISuggestion(@RequestBody AISuggestionRequest request) {
        String result = aiSuggestionService.getAISuggestion(request.getCode(), request.getLanguage());
        return ResponseEntity.ok(result);
    }
}
