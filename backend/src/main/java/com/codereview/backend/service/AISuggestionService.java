package com.codereview.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class AISuggestionService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    // --- Gemini API keys (rotate if one fails) ---
    private final String[] GEMINI_KEYS = {
            "AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y",
            "AIzaSyCGm1uGRJhEfl9cKPGNOSku4Ky1uL2G-fU"
    };
    private final AtomicInteger keyIndex = new AtomicInteger(0);

    // --- Rate limiter ---
    private long lastGeminiCall = 0;
    private static final long GEMINI_COOLDOWN = 30_000; // 30 seconds

    public String getAISuggestion(String code, String language) {
        try {
            long now = System.currentTimeMillis();

            // --- Rate limit check ---
            long remaining = GEMINI_COOLDOWN - (now - lastGeminiCall);
            if (remaining > 0) {
                return "⏳  Please try again after " + (remaining / 1000) + " seconds.";
            }

            // --- Try all Gemini keys in rotation ---
            for (int i = 0; i < GEMINI_KEYS.length; i++) {
                String apiKey = GEMINI_KEYS[(keyIndex.getAndIncrement()) % GEMINI_KEYS.length];
                try {
                    String response = callGemini(apiKey, code, language);
                    if (response != null && !response.isEmpty()) {
                        lastGeminiCall = System.currentTimeMillis(); // ✅ cooldown only on success
                        return response;
                    }
                } catch (Exception e) {
                    System.out.println("[Gemini Error with key " + apiKey + "] " + e.getMessage());
                    // continue with next key
                }
            }

            // --- If all Gemini keys fail → fallback ---
            return safeTinyLLaMA(code, language);

        } catch (Exception e) {
            System.out.println("[AISuggestionService Error] " + e.getMessage());
            return safeTinyLLaMA(code, language);
        }
    }

    private String callGemini(String apiKey, String code, String language) throws Exception {
        String url = "https://generativelanguage.googleapis.com/v1beta/models/"
                + "gemini-1.5-flash:generateContent?key=" + apiKey;

        // --- Build prompt ---
        String prompt =
                "You are a senior software engineer and code reviewer. " +
                        "Review the following " + language + " code carefully. " +
                        "If the input is not related to programming or code review, respond only with: '❌ Cannot process non-code input'.\n\n" +
                        "When valid code is given, respond in very concise points:\n" +
                        "1. ✅ Errors (if any) OR Output of the code\n" +
                        "2. ⚠️ Bad Practices\n" +
                        "3. 💡 Suggestions for Improvement\n\n" +
                        "Code:\n" + code;

        // --- Request body ---
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

        JsonNode root = objectMapper.readTree(response.getBody());
        return root.path("candidates")
                .get(0)
                .path("content")
                .path("parts")
                .get(0)
                .path("text")
                .asText();
    }

    // --- TinyLLaMA Fallback with safety wrapper ---
    private String safeTinyLLaMA(String code, String language) {
        try {
            String text = callTinyLLaMA(code, language);
            return (text == null || text.isEmpty())
                    ? "⚠️ TinyLLaMA returned empty response."
                    : text;
        } catch (Exception e) {
            return "⚠️ try later: " + e.getMessage();
        }
    }

    private String callTinyLLaMA(String code, String language) throws Exception {
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

        JsonNode root = objectMapper.readTree(response.getBody());
        return root.path("response").asText();
    }
}
