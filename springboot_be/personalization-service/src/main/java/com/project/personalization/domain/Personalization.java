package com.project.personalization.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "Personalization")
public class Personalization {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long personalizationId;
    private Long userId;
    private String references;

    public Personalization(){
    }

    public Personalization(Long personalizationId, String references, Long userId) {
        this.personalizationId = personalizationId;
        this.references = references;
        this.userId = userId;
    }

    public Long getPersonalizationId() {
        return personalizationId;
    }

    public void setPersonalizationId(Long personalizationId) {
        this.personalizationId = personalizationId;
    }

    public String getReferences() {
        return references;
    }

    public void setReferences(String references) {
        this.references = references;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }
}
