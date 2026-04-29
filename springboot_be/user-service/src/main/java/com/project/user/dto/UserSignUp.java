package com.project.user.dto;

public class UserSignUp {

    private String username;
    private String email;
    private String password;
    private String phone;
    private String fullName;
    private String userType;

    public UserSignUp() {}

    public UserSignUp(String username, String email, String password, String phone, String userType, String fullName) {
        this.username = username;
        this.email = email;
        this.password = password;
        this.phone = phone;
        this.userType = userType;
        this.fullName = fullName;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getUserType() {
        return userType;
    }

    public void setUserType(String userType) {
        this.userType = userType;
    }
}
