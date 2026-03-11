package com.project.personalization;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
public class PersonalizationApplication {
    public static void main(String[] args) {
        SpringApplication.run(PersonalizationApplication.class, args);
    }
}
