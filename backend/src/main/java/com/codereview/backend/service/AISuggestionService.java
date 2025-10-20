package com.codereview.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class AISuggestionService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    // --- Configuration ---
    private final String[] GEMINI_KEYS = {
            "",
            ""
    };
    private final AtomicInteger keyIndex = new AtomicInteger(0);
    private long lastGeminiCall = 0;
    private static final long GEMINI_COOLDOWN = 30_000; // 30 seconds
    private static final long GEMINI_MIN_RESPONSE_DELAY = 10_000; // 10 seconds delay (blocks current thread)

    // --- Public Service Method ---
    public String getAISuggestion(String code, String language) {
        long now = System.currentTimeMillis();

        // 1. Rate limit check (RETURN immediately if limited)
        long remaining = GEMINI_COOLDOWN - (now - lastGeminiCall);
        if (remaining > 0) {
            return "⏳ Please try again after " + (remaining / 1000) + " seconds.";
        }

        // --- 2. Try Gemini (Rotating Keys) ---
        String geminiResponse = tryGeminiWithRotation(code, language);
        if (geminiResponse != null) {
            lastGeminiCall = System.currentTimeMillis(); // Cooldown only starts on a successful response
            return geminiResponse;
        }

        // --- 3. Try TinyLLaMA Fallback ---
        System.out.println("[DEBUG] Gemini failed. Attempting TinyLLaMA fallback.");
        String tinyLlamaResponse = safeTinyLLaMA(code, language);
        if (tinyLlamaResponse != null) {
            return tinyLlamaResponse;
        }

        // --- 4. Final Static Fallback ---
        System.out.println("[DEBUG] TinyLLaMA failed. Returning static fallback.");
        return generateStaticFallback();
    }

    private String tryGeminiWithRotation(String code, String language) {
        long startTime = System.currentTimeMillis();
        String finalResponse = null;

        for (int i = 0; i < GEMINI_KEYS.length; i++) {
            String apiKey = GEMINI_KEYS[(keyIndex.getAndIncrement()) % GEMINI_KEYS.length];
            try {
                finalResponse = callGemini(apiKey, code, language);
                if (finalResponse != null && !finalResponse.isEmpty()) {
                    // Success! Break and return the response.
                    break;
                }
            } catch (Exception e) {
                // Log failure for this key, but continue to the next one
                System.out.println("[DEBUG] Gemini key failure (" + (i + 1) + "/" + GEMINI_KEYS.length + "): " + e.getMessage());
            }
        }

        // --- Enforce Minimum Delay ---
        long elapsedTime = System.currentTimeMillis() - startTime;
        long timeToWait = GEMINI_MIN_RESPONSE_DELAY - elapsedTime;
        if (timeToWait > 0) {
            System.out.println("[DEBUG] Enforcing minimum Gemini delay. Sleeping for " + timeToWait + "ms.");
            try {
                Thread.sleep(timeToWait);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        return finalResponse;
    }

    private String callGemini(String apiKey, String code, String language) throws Exception {
        String url = "https://generativelanguage.googleapis.com/v1beta/models/"
                + "gemini-2.5-flash:generateContent?key=" + apiKey;

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

        if (response.getStatusCode() != HttpStatus.OK) {
            throw new Exception("Gemini API returned status: " + response.getStatusCode());
        }

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
            return callTinyLLaMA(code, language);
        } catch (ResourceAccessException e) {
            // Log connection/timeout errors internally
            System.out.println("[DEBUG] TinyLLaMA connection failure/timeout: " + e.getMessage());
            return null; // Null indicates failure, prompting static fallback
        } catch (Exception e) {
            // Log other errors internally
            System.out.println("[DEBUG] TinyLLaMA generic failure: " + e.getMessage());
            return null; // Null indicates failure, prompting static fallback
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

        if (response.getStatusCode() != HttpStatus.OK) {
            throw new Exception("TinyLLaMA API returned status: " + response.getStatusCode());
        }

        JsonNode root = objectMapper.readTree(response.getBody());
        String result = root.path("response").asText();

        if (result.isEmpty() || result.isBlank()) {
            // Treat empty response as failure
            throw new Exception("TinyLLaMA response was empty.");
        }
        return result;
    }

    // --- Final Static Fallback (Tier 3) ---
    private String generateStaticFallback() {
        return "❌ Server error Please try again later.\n\n"
                + " Here are some general best practices:\n"
                + "1. Clarity: Use meaningful variable and function names (e.g., `calculateTotal` instead of `calc`).\n"
                + "2. Modularity (Single Responsibility): Break down large functions into smaller, single-purpose units.\n"
                + "3. Error Handling: Always validate inputs and handle potential exceptions gracefully to prevent crashes.\n"
                + "4. DRY Principle: Avoid code duplication (Don't Repeat Yourself) by leveraging functions, loops, or shared utility classes.\n"
                + "5. Testing: Write unit tests for critical components to ensure code works as expected and prevent future regressions.";
    }
}
