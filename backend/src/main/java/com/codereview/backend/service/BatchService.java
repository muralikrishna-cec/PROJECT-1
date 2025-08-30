package com.codereview.backend.service;

import com.codereview.backend.util.BatchRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;


@Service
public class BatchService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String PYTHON_URL = "http://localhost:8000/batch";

    public ResponseEntity<String> analyzeRepo(BatchRequest request) {
        // Forward same JSON to Python
        return restTemplate.postForEntity(PYTHON_URL, request, String.class);
    }
}


