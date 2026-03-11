package com.project.personalization.repository;

import com.project.personalization.domain.Personalization;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;

import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface PersonalizationRepository extends JpaRepository<Personalization, Long> {

    @Query("SELECT p FROM Personalization p WHERE p.id =:id")
    Personalization getPersonalizationById(@Param("id") Long id);
}
