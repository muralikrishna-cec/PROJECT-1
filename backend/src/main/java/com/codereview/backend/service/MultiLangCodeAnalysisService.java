package com.codereview.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.HashMap;
import java.util.Map;

@Service
public class MultiLangCodeAnalysisService {

    private final RestTemplate restTemplate;

    public MultiLangCodeAnalysisService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public String analyze(String code, String language) {
        String pythonServiceUrl = "http://localhost:6000/analyze";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> payload = new HashMap<>();
        payload.put("code", code);
        payload.put("language", language);

        HttpEntity<Map<String, String>> requestEntity = new HttpEntity<>(payload, headers);
        ResponseEntity<Map> response = restTemplate.exchange(
                pythonServiceUrl, HttpMethod.POST, requestEntity, Map.class);

        if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
            return response.getBody().get("report").toString();
        } else {
            return "❌ Error from multi-language analysis service";
        }
    }
}

