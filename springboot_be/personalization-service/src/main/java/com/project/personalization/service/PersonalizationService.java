package com.project.personalization.service;

import com.project.personalization.domain.Personalization;

import java.util.List;

public interface PersonalizationService {

    Personalization getPersonalizationById(Long personalizationId);

    void addPersonalization(Personalization personalization);

    void clearPersonalization(Long userId, Long perId);

    List<Personalization> getAllPer();

    List<Personalization> getPersonalizationByUserId(Long userId);
}
