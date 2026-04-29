package com.project.personalization.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "Personalization")
public class Personalization {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long personalizationId;
    private Long userId;
    private String myContent;

    public Personalization(){
    }

    public Personalization(Long personalizationId, Long userId, String myContent) {
        this.personalizationId = personalizationId;
        this.userId = userId;
        this.myContent = myContent;
    }

    public Long getPersonalizationId() {
        return personalizationId;
    }

    public void setPersonalizationId(Long personalizationId) {
        this.personalizationId = personalizationId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getMyContent() {
        return myContent;
    }

    public void setMyContent(String myContent) {
        this.myContent = myContent;
    }
}
