package com.codereview.backend.service;

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class AISuggestionService {

    public String getAISuggestion(String code, String language) {
        try {
            String url = "http://localhost:5000/chat"; // !

            RestTemplate restTemplate = new RestTemplate();

            Map<String, String> request = new HashMap<>();
            request.put("code", code);
            request.put("language", language);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    String.class
            );

            return response.getBody();
        } catch (Exception e) {
            return "⚠️ Error talking to TinyLLaMA: " + e.getMessage();
        }
    }
}
