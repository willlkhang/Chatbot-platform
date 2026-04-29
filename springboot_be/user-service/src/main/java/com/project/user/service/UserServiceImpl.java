package com.project.user.service;

import com.project.base.domain.User;
import com.project.base.outputDto.UserResponse;
import com.project.user.repository.UserRepository;
import com.project.user.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class UserServiceImpl implements UserService{

    @Autowired
    UserRepository userRepository;
    @Autowired
    UserMapper userMapper;

    @Override
    public List<UserResponse> getAllUsers() {
        List<User> users = userRepository.getAllUser();
        return users.stream().map(a -> userMapper.toResponse(a)).collect(Collectors.toList());
    }

    @Override
    public User getUserById(Long id) {
        return userRepository.findUserByUserId(id);
    }

    @Override
    public User getUserByUsername(String name) {
        return userRepository.getUserByUsername(name);
    }

    @Override
    public void saveUser(User user) {
        userRepository.save(user);
    }

    @Override
    public boolean isDuplicatedUsername(String username) {
        User user = userRepository.findUserByUsername(username);
        return user != null;
    }
    @Override
    public boolean isDuplicatedEmail(String email) {
        User user = userRepository.findUserByUserEmail(email);
        return user != null;
    }

}
