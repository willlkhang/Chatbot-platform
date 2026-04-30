package com.project.chat.service;
import java.util.List;

import com.project.chat.domain.Chat;
import com.project.chat.domain.ChatMessage;
import com.project.chat.repository.ChatRepository;
import jakarta.transaction.Transactional;
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
    public List<Chat> getChatsByUserId(Long userId) {
        return chatRepository.findChatsByUserId(userId);
    }

    @Override
    @Transactional
    public Chat appendMessageToConversation(Long chatId, Long userId, String senderRole, String content) {
        Chat chat = chatRepository.findByChatIdAndUserId(chatId, userId)
                .orElseThrow(() -> new RuntimeException("Chat is not found or unauthorized"));

        ChatMessage newMessage = new ChatMessage(senderRole, content);
        chat.getMessages().add(newMessage);
        return chatRepository.save(chat);
    }

    @Override
    public void createChat(Chat chat) {
        chatRepository.save(chat);
    }

    @Override
    public void deleteChat(Long chatId, Long userId) {
        Chat chat = chatRepository.findByChatIdAndUserId(chatId, userId)
                .orElseThrow(() -> new RuntimeException("Chat is not found or unauthorized"));
        chatRepository.delete(chat);
    }

    @Override
    public List<Chat> getAllChat() {
        return chatRepository.findAll();
    }
}
