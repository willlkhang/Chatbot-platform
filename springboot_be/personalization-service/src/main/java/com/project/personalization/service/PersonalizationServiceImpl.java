package com.project.personalization.service;

import com.project.personalization.domain.Personalization;

import com.project.personalization.repository.PersonalizationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;


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

    @Override
    public List<Personalization> getAllPer() {

        List<Personalization> pers = personalizationRepository.findAll();
        return pers.stream().collect(Collectors.toList());
    }

    @Override
    public List<Personalization> getPersonalizationByUserId(Long userId) {
        List<Personalization> pers = personalizationRepository.getPersonalizationByUserId(userId);

        return pers.stream().collect(Collectors.toList());
    }
}
