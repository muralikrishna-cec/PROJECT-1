package com.codereview.backend.util;


public class BatchRequest {
    private String type;
    private String github_url;

    // Getters and setters
    public String getType() {
        return type;
    }
    public void setType(String type) {
        this.type = type;
    }

    public String getGithub_url() {
        return github_url;
    }
    public void setGithub_url(String github_url) {
        this.github_url = github_url;
    }
}
