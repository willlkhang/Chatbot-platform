package com.project.chat.service;

import com.project.chat.domain.Chat;

import java.util.List;

public interface ChatService {

    Chat getChatById(Long chatId);
    Chat getChatByUserId(Long userId);

    void createChat(Chat chat);

    Chat appendMessageToConversation(Long chatId, Long userId, String senderRole, String content);

    List<Chat> getAllChat();
}
