package com.project.user.service;

import com.project.base.domain.User;
import com.project.base.outputDto.UserResponse;
import com.project.user.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserServiceImpl implements UserService{

    @Autowired
    UserRepository userRepository;

    @Override
    public List<UserResponse> getAllUsers() {
        List<User> users = userRepository.getAllUser();
        return null;
    }

    @Override
    public User getUserById(Long id) {
        userRepository.findUserByUserId(id);
    }

    @Override
    public User getUserByUsername(String name) {
        userRepository.getUserByUsername(name);
    }
}
