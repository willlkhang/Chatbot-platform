package com.project.personalization.controller;

import com.project.personalization.domain.Personalization;
import com.project.personalization.service.PersonalizationService;

//rest api spring boot group
import feign.Response;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.repository.query.Param;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
//@RequestMapping("/api/personalization")
public class PersonalizationController {

    @Autowired
    private PersonalizationService personalizationService;

    @GetMapping("/user/{userId}")
    public ResponseEntity<?> findPersonalizationsByUserId(@PathVariable Long userId){
        List<Personalization> pers = personalizationService.getPersonalizationByUserId(userId);

        if (pers == null){
            return ResponseEntity.ok("There is not personalization for this user");
        }
        else
            return ResponseEntity.ok().body(pers);
    }

    @PostMapping("/adding")
    public ResponseEntity<?> addPersonalization(@RequestBody Personalization per) {
        personalizationService.addPersonalization(per);
        return ResponseEntity.ok().body(per);
    }

    @PostMapping("/deleting")
    public ResponseEntity<?> deletePersonalization(@RequestParam Long userId, Long perId) {

        String message = String.format("Personalization %d from user %d is removed", userId, perId);

        personalizationService.clearPersonalization(userId, perId);
        return ResponseEntity.ok(message);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getPersonalizationById(@PathVariable Long id) {
        Personalization per = personalizationService.getPersonalizationById(id);

        if (per == null){
            return ResponseEntity.ok("There is not personal yet (Ignore this instruction)");
        }
        else{
            return ResponseEntity.ok().body(per);
        }
    }

    @GetMapping("/all")
    public ResponseEntity<?> getAllPers(){
        List<Personalization> list = personalizationService.getAllPer();

        if (list.isEmpty()){
            return ResponseEntity.ok().body("There is on personalization yet");
        }
        else {
            return ResponseEntity.ok().body(list);
        }
    }
}
