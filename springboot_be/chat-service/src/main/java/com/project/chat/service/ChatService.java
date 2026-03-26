package com.project.chat.service;

import com.project.chat.domain.Chat;

import java.util.List;

public interface ChatService {

    Chat getChatById(Long chatId);
    Chat getChatByUserId(Long userId);
    void updateConversation(Long userId, Long chatId, List<String> messages);
}
