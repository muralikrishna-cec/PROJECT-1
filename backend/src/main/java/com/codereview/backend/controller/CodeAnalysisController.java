package com.codereview.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class CodeAnalysisController {

    @PostMapping("/analyze")
    public ResponseEntity<String> analyzeCode(@RequestBody String code) {
        // For now, just return dummy success
        return ResponseEntity.ok("Static analysis result will go here");
    }
}
