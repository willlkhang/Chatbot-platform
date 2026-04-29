package com.project.user.controller;

// user domain group
import com.project.base.domain.User;
import com.project.base.outputDto.UserResponse;
import com.project.user.dto.UserSignUp;
import com.project.user.service.UserService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;

import org.springframework.web.bind.annotation.*;

import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;

@RestController
//@RequestMapping("/api/user")
public class UserController {

    @Autowired
    UserService userService;

    @Autowired
    PasswordEncoder passwordEncoder;

    @GetMapping("/all")
    public ResponseEntity<?> getAllUsers() {
        List<UserResponse> userEntities = userService.getAllUsers();

        if (userEntities == null){
            return ResponseEntity.ok("There is no users stored in the database");
        }
        return ResponseEntity.ok().body(userEntities);
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        User user = userService.getUserById(id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok().body(user);
    }

    @PostMapping("/save")
    public ResponseEntity<User> saveUser(@RequestBody User user) {
        userService.saveUser(user);
        return ResponseEntity.ok().body(user);
    }

    @PostMapping("/registery")
    public ResponseEntity<?> registerNewUser(@RequestBody UserSignUp userSignUp){

        if (!userService.isDuplicatedEmail(userSignUp.getEmail()) ||
                !userService.isDuplicatedUsername(userSignUp.getUsername())){
            User user = new User();
            user.setEmail(userSignUp.getEmail());
            user.setUsername(userSignUp.getUsername());
            user.setPassword(passwordEncoder.encode(userSignUp.getPassword()));
            user.setFullName(userSignUp.getFullName());
            user.setPhone(userSignUp.getPhone());

            userService.saveUser(user);

            return ResponseEntity.ok().body(user);
        }
        else {
            return ResponseEntity.ok("This Username or email is already exited");
        }
    }
}
