package com.project.chat.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;

@Embeddable
public class ChatMessage {

    private String senderRole;

    @Column(columnDefinition = "TEXT")
    private String content;

    public ChatMessage(){}

    public ChatMessage(String senderRole, String content) {
        this.senderRole = senderRole;
        this.content = content;
    }

    public String getSenderRole() {
        return senderRole;
    }

    public void setSenderRole(String senderRole) {
        this.senderRole = senderRole;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
