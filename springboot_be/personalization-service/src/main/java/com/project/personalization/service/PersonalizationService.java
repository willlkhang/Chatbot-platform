package com.project.personalization.service;

import com.project.personalization.domain.Personalization;

public interface PersonalizationService {

    Personalization getPersonalizationById(Long personalizationId);
}
