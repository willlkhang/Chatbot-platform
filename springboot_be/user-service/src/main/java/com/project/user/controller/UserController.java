package com.project.user.controller;

// user domain group
import com.project.base.domain.User;
import com.project.user.service.UserService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;

import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import org.springframework.security.crypto.password.PasswordEncoder;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    UserService userService;

    @Autowired
    PasswordEncoder passwordEncoder;

    public ResponseEntity<?> createUser(@RequestBody User user){
        userService.createUser(user);

        return ResponseEntity.ok().body(user);
    }
}
