package com.project.chat.domain;

import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "Chat")
public class Chat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long chatId;
    private Long userId;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "chat_messages", joinColumns = @JoinColumn(name = "chat_id"))
    @OrderColumn(name = "message_order")
    private List<ChatMessage> messages = new ArrayList<>();

    public Chat() {}

    public Chat(Long chatId, Long userId, List<ChatMessage> messages) {
        this.chatId = chatId;
        this.userId = userId;
        this.messages = messages;
    }

    public Long getChatId() {
        return chatId;
    }

    public void setChatId(Long chatId) {
        this.chatId = chatId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public List<ChatMessage> getMessages() {
        return messages;
    }

    public void setMessages(List<ChatMessage> messages) {
        this.messages = messages;
    }
}
