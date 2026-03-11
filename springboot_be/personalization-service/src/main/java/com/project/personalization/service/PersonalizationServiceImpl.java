package com.project.personalization.service;

import com.project.personalization.domain.Personalization;

import com.project.personalization.repository.PersonalizationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;


@Service
public class PersonalizationServiceImpl implements PersonalizationService {

    @Autowired
    private PersonalizationRepository personalizationRepository;

    @Override
    public Personalization getPersonalizationById(Long personalizationId) {
        return  personalizationRepository.getPersonalizationById(personalizationId);
    }

    @Override
    public void addPersonalization(Personalization personalization) {
        personalizationRepository.save(personalization);
    }

    @Override
    public void clearPersonalization(Long userId, Long perId) {
        Personalization entity = personalizationRepository.getPersonalizationByUserAndId(userId, perId);
        personalizationRepository.delete(entity);
    }
}
