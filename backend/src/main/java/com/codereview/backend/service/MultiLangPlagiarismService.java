package com.codereview.backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class MultiLangPlagiarismService {

    private final RestTemplate restTemplate;

    @Value("${python.microservice.plagiarism.url:http://localhost:8000/plagiarism}")
    private String pythonServiceUrl;

    public MultiLangPlagiarismService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map<String, Object> checkWithPythonMicroservice(String code1, String code2, String language) {
        try {
            Map<String, String> payload = new HashMap<>();
            payload.put("code1", code1);
            payload.put("code2", code2);
            payload.put("language", language);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, String>> entity = new HttpEntity<>(payload, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(pythonServiceUrl, entity, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                Map<String, Object> error = new HashMap<>();
                error.put("verdict", "❌ Error from Python microservice.");
                error.put("details", response.getBody());
                return error;
            }

        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("verdict", "❌ Exception occurred while contacting Python microservice.");
            error.put("error", e.getMessage());
            return error;
        }
    }
}
