package com.codereview.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class AISuggestionService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public String getAISuggestion(String code, String language) {
        try {
            // Gemini API URL
            String url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y";

            // ✅ Build prompt
            // ✅ Build prompt
            String prompt =
                    "You are a senior software engineer and code reviewer. " +
                            "Review the following " + language + " code carefully. " +
                            "If the input is not related to programming or code review, simply respond with: '❌ Cannot process non-code input'.\n\n" +
                            "When valid code is given, respond in a **very concise and effective manner**, strictly using points only:\n" +
                            "1. ✅ Errors (if any) OR the Output of the code\n" +
                            "2. ⚠️ Bad Practices\n" +
                            "3. 💡 Suggestions for Improvement\n\n" +
                            "Code:\n" + code;


            // ✅ Build request body
            Map<String, Object> request = new HashMap<>();
            Map<String, Object> part = new HashMap<>();
            part.put("text", prompt);

            Map<String, Object> content = new HashMap<>();
            content.put("parts", new Object[]{part});

            request.put("contents", new Object[]{content});

            String requestJson = objectMapper.writeValueAsString(request);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<String> entity = new HttpEntity<>(requestJson, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    String.class
            );

            // ✅ Extract only the text response
            JsonNode root = objectMapper.readTree(response.getBody());
            String text = root.path("candidates")
                    .get(0)
                    .path("content")
                    .path("parts")
                    .get(0)
                    .path("text")
                    .asText();

            return text.isEmpty() ? "⚠️  no response." : text;

        } catch (Exception e) {
            // ✅ Backup: call TinyLLaMA if Gemini fails
            return "⚠️ ⚠️ Try Again...\n\n" + callTinyLLaMA(code, language);
        }
    }

    private String callTinyLLaMA(String code, String language) {
        try {
            String url = "http://localhost:5000/chat";

            Map<String, String> request = new HashMap<>();
            request.put("prompt",
                    "You are a senior software engineer. Analyze this " + language + " code and provide:\n"
                            + "1. ✅ Errors\n2. ⚠️ Bad Practices\n3. 💡 Suggestions\n\n"
                            + code
            );

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    String.class
            );

            // ✅ Parse JSON and extract 'response' field
            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(response.getBody());
            String text = root.path("response").asText();

            return text.isEmpty() ? "⚠️ TinyLLaMA returned empty response." : text;

        } catch (Exception e) {
            return "⚠️ Failed to generate... try again: " + e.getMessage();
        }
    }

}
