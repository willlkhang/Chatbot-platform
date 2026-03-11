package com.project.personalization.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "Personalization")
public class Personalization {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long Id;
    private Long userId;
    private String references;

    public Personalization(){
    }

    public Personalization(String references, Long userId, Long id) {
        this.references = references;
        this.userId = userId;
        Id = id;
    }

    public Long getId() {
        return Id;
    }

    public void setId(Long id) {
        Id = id;
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
