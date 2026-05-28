package com.project.chat.controller;

import com.project.chat.domain.Chat; //chat aggregate (conversation)
import com.project.chat.dto.ChatMessageRequest; //incoming message payload (role + content)
import com.project.chat.service.ChatService; //service layer that talks to repository
import org.springframework.beans.factory.annotation.Autowired; //DI for ChatService
import org.springframework.http.ResponseEntity; //HTTP response wrapper
import org.springframework.web.bind.annotation.*; //REST annotations

import java.util.List;

@RestController
//@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    ChatService chatService;

    @PostMapping("/create")
    public ResponseEntity<?> createChat(@RequestBody Chat chat){
        //create a new chat record (usually the first time user starts a conversation)
        chatService.createChat(chat); //persist chat
        return ResponseEntity.ok().body(chat); //return saved chat object
    }

    @GetMapping("/user/{userId}/all")
    public ResponseEntity<?> getChatsByUserId(@PathVariable Long userId){
        //fetch all chats that belong to a user (used by chat history list)
        List<Chat> chats = chatService.getChatsByUserId(userId); //read from DB
        return ResponseEntity.ok().body(chats); //return list of chats
    }

    @GetMapping("/{userId}")
    public ResponseEntity<?> getChatByUserId(@PathVariable Long userId){
        //get a single chat for a user (depends on your repository logic; might be "latest chat")
        Chat chat = chatService.getChatByUserId(userId); //service decides which chat to return
        if(chat == null){ //no chat found for this user
            return ResponseEntity.notFound().build(); //404
        }
        return ResponseEntity.ok().body(chat); //return chat
    }

    @GetMapping("/user/{id}")
    public ResponseEntity<?> getChatById(@PathVariable Long id){
        //get chat by chat id (direct lookup)
        Chat chat = chatService.getChatById(id); //read from DB
        if(chat == null){ //no chat row with that id
            return ResponseEntity.notFound().build(); //404
        }
        return ResponseEntity.ok().body(chat); //return chat
    }

    @PostMapping("/{chatId}/user/{userId}/messages")
    public ResponseEntity<?> updateConversation(@PathVariable Long chatId,
                                                @PathVariable Long userId,
                                                @RequestBody ChatMessageRequest incomingMessage){
        //append a new message to an existing conversation (chatId+userId is a simple auth check)
        Chat updatedChat = chatService.appendMessageToConversation(
                chatId,
                userId,
                incomingMessage.getSenderRole(),
                incomingMessage.getContent()
        );

        return ResponseEntity.ok().body(updatedChat); //return updated conversation
    }

    @GetMapping("/all")
    public ResponseEntity<?> getallChat(){
        //admin/debug endpoint: fetch every chat in database
        List<Chat> chats = chatService.getAllChat(); //read all

        return ResponseEntity.ok().body(chats);
    }

    @DeleteMapping("/{chatId}/user/{userId}")
    public ResponseEntity<?> deleteChat(@PathVariable Long chatId, @PathVariable Long userId) {
        //delete chat (the userId check prevents deleting other users' chats)
        chatService.deleteChat(chatId, userId); //service enforces "exists + authorized"
        return ResponseEntity.noContent().build(); //204
    }
}
