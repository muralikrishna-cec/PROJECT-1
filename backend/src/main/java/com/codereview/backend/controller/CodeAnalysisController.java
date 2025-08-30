package com.codereview.backend.controller;

import com.codereview.backend.model.AISuggestionRequest;
import com.codereview.backend.model.PlagiarismRequest;
import com.codereview.backend.service.*;
import com.codereview.backend.util.BatchRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;


@RestController
@RequestMapping("/api")
public class CodeAnalysisController {

    @Autowired
    private CodeAnalysisService codeAnalysisService;

    @Autowired
    private MultiLangCodeAnalysisService multiLangService;

    @Autowired
    private PlagiarismService plagiarismService;

    @Autowired
    private AISuggestionService aiSuggestionService;

    @Autowired
    private MultiLangPlagiarismService multiLangPlagiarismService;

    @Autowired
    private  BatchService batchService;

    @PostMapping("/analyze")
    public ResponseEntity<Map<String, Object>> analyzeCode(@RequestBody Map<String, String> request) {
        String code = request.get("code");
        String language = request.get("language");

        Map<String, Object> result;

        if ("java".equalsIgnoreCase(language)) {
            // Java analyzer already returns Map<String, Object>
            result = codeAnalysisService.analyze(code);
        } else {
            result = multiLangService.analyze(code, language);
        }

        return ResponseEntity.ok(result);
    }




    @PostMapping("/plagiarism")
    public ResponseEntity<Map<String, Object>> checkPlagiarism(@RequestBody PlagiarismRequest request) {
        Map<String, Object> report;

        if ("java".equalsIgnoreCase(request.getLanguage())) {
            report = plagiarismService.getPlagiarismReport(request.getCode1(), request.getCode2());
        } else {
            report = multiLangPlagiarismService.checkWithPythonMicroservice(
                    request.getCode1(), request.getCode2(), request.getLanguage()
            );
        }

        return ResponseEntity.ok(report);
    }

    @PostMapping("/ai-suggest")
    public ResponseEntity<String> getAISuggestion(@RequestBody AISuggestionRequest request) {
        String result = aiSuggestionService.getAISuggestion(request.getCode(), request.getLanguage());
        return ResponseEntity.ok(result);
    }

    /**
     * Case 1: Analyze repository from GitHub link
     */
    @PostMapping("/batch")
    public ResponseEntity<String> analyzeRepoFromGithub(@RequestBody BatchRequest request) {
        if ("github".equalsIgnoreCase(request.getType())) {
            return batchService.analyzeRepo(request);
        }
        // Later we’ll add "zip" type support here
        return ResponseEntity.badRequest().body("Unsupported type: " + request.getType());
    }

    /* ** Case 2: Analyze repository from uploaded ZIP file */


}
