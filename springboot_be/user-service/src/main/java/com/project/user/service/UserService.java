package com.project.user.service;

import com.project.base.domain.User;
import com.project.base.outputDto.UserResponse;

import java.util.List;

public interface UserService {

    User getUserByUsername(String name);
    User getUserById(String id);
    List<UserResponse> getAllUsers();

}
