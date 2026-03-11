package com.project.personalization.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "Personalization")
public class Personalization {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long personalizationId;
    private Long userId;
    private String myReferences;

    public Personalization(){
    }

    public Personalization(Long personalizationId, Long userId, String myReferences) {
        this.personalizationId = personalizationId;
        this.userId = userId;
        this.myReferences = myReferences;
    }

    public Long getPersonalizationId() {
        return personalizationId;
    }

    public void setPersonalizationId(Long personalizationId) {
        this.personalizationId = personalizationId;
    }

    public String getMyReferences() {
        return myReferences;
    }

    public void setMyReferences(String myReferences) {
        this.myReferences = myReferences;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }
}
