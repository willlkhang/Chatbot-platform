package com.project.user.mapper;

import com.project.base.domain.User;
import com.project.base.outputDto.UserResponse;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface UserMapper {

    UserResponse toResponse(User user);
}