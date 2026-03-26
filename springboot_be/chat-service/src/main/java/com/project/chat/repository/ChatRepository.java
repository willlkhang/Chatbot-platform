package com.project.chat.repository;

import com.project.chat.domain.Chat;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;

import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ChatRepository extends JpaRepository<Chat, Long> {

    @Query("SELECT c FROM Chat c WHERE c.userId =:userId")
    Chat findChatByUserId(@Param("userId") Long userId);

    @Query("SELECT c FROM Chat c WHERE c.chatId=:chatId")
    Chat findChatById(@Param("chatId") Long chatId);

    @Transactional
    @Modifying
    @Query(value = "UPDATE Chat c SET c.messages=:messages WHERE c.chatId =:chatId")
    void updateConversation(@Param("chatId") Long chatId,
                            @Param("messages") List<String> messages);
}
