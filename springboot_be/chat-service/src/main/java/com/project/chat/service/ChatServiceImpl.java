package com.project.chat.service;
import java.util.List;

import com.project.chat.domain.Chat;
import com.project.chat.repository.ChatRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

@Service
public class ChatServiceImpl implements ChatService{

    @Autowired
    ChatRepository chatRepository;

    @Override
    public Chat getChatById(Long chatId) {
        return chatRepository.findChatById(chatId);
    }

    @Override
    public Chat getChatByUserId(Long userId) {
        return chatRepository.findChatByUserId(userId);
    }

    @Override
    public void updateConversation(Long userId, Long chatId, List<String> messages) {
        chatRepository.updateConversation(chatId, userId, messages);
    }
}
