package com.project.user.service;

import com.project.base.domain.User;
import com.project.base.outputDto.UserResponse;

import java.util.List;

public class UserServiceImpl implements UserService{
    @Override
    public List<UserResponse> getAllUsers() {
        return List.of();
    }

    @Override
    public User getUserById(String id) {
        return null;
    }

    @Override
    public User getUserByUsername(String name) {
        return null;
    }
}
