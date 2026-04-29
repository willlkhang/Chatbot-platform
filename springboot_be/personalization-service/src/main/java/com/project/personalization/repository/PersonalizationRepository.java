package com.project.personalization.repository;

import com.project.personalization.domain.Personalization;
//import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;

//import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PersonalizationRepository extends JpaRepository<Personalization, Long> {

    @Query("SELECT p FROM Personalization p WHERE p.personalizationId =:id")
    Personalization getPersonalizationById(@Param("id") Long id);

    @Query("SELECT p FROM Personalization p WHERE p.personalizationId =:perId AND p.userId =:userId")
    Personalization getPersonalizationByUserAndId(@Param("userId") Long userId, @Param("perId") Long perId);

    @Query("SELECT p FROM Personalization p WHERE  p.userId =:userId")
    List<Personalization> getPersonalizationByUserId(@Param("userId") Long userId);
    //List<Personalization> findByUserId(Long userId);

    @Query("SELECT p FROM Personalization p")
    List<Personalization> getAllPer();
}
