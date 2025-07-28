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
           // request.put("prompt", "You are a senior software engineer. Analyze the following " + language + " code for errors, bad practices, and improvements. Give code suggestions and explain clearly like a mentor.");
            request.put("prompt",
                    "You are a senior software engineer and code reviewer. Your job is to review the following " + language + " code carefully. " +
                            "Identify errors, bad practices, and improvements. Explain everything in simple language like you're mentoring a beginner. " +
                            "Give suggestions clearly with code blocks and explanations. If applicable, rewrite the improved version of the code at the end.\n\n" +
                            "Respond in the following format:\n" +
                            "1. ✅ Errors (if any)\n" +
                            "2. ⚠️ Bad Practices\n" +
                            "3. 💡 Suggestions for Improvement\n" +
                            "4. ✨ Improved Code (in a ```" + language + "``` code block)\n\n" +
                            "Now analyze the following code:\n\n" +
                            code
            );

           // request.put("code", code);
            // request.put("language", language);

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
