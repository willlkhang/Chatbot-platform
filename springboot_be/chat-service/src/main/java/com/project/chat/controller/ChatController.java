package com.project.chat.controller;

import com.project.chat.domain.Chat;
import com.project.chat.service.ChatService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    ChatService chatService;

    @PostMapping("/create")
    public ResponseEntity<?> createChat(@RequestBody Chat chat){
        chatService.createChat(chat);
        return ResponseEntity.ok().body(chat);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getChatByUserId(@PathVariable Long userId){
        Chat chat = chatService.getChatByUserId(userId);
        if(chat == null){
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok().body(chat);
    }

    @GetMapping("/user/{id}")
    public ResponseEntity<?> getChatById(@PathVariable Long id){
        Chat chat = chatService.getChatById(id);
        if(chat == null){
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok().body(chat);
    }

    @PostMapping("/user/{chatId}/chat/{userId}")
    public ResponseEntity<?> updateConversation(@RequestParam Long chatId,
                                                @RequestParam Long userId,
                                                @RequestParam List<String> messages){
        chatService.updateConversation(chatId, userId, messages);

        return ResponseEntity.ok(messages);
    }
}
