package com.project.auth.controller;

import com.project.base.loginDto.LoginRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@RestController
public class AuthController {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${spring.profiles.active}")
    private String whoami;

    @Value("${spring.app.oauth-url}")
    private String oauthTokenUrl;

    @Value("${spring.security.oauth2.resourceserver.jwt.client-id:project}")
    private String clientId;

    @Value("${spring.security.oauth2.resourceserver.jwt.client-secret:secret}")
    private String clientSecret;

    @GetMapping("/test")
    public ResponseEntity<?> test(){
        return ResponseEntity.ok(whoami); //test print value from yml properties
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        String url = this.oauthTokenUrl;

        //prepare as setting up in Postman
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
        headers.setBasicAuth(clientId, clientSecret);

        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("grant_type", "password");
        body.add("username", request.getUsername());
        body.add("password", request.getPassword());

        HttpEntity<MultiValueMap<String, String>> entity = new HttpEntity<>(body, headers);

        try {
            // "Map.class" is a generic way to catch whatever JSON comes back (access_token, etc.)
            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    Map.class
            );
            return ResponseEntity.ok(response.getBody());
        }   catch (HttpClientErrorException e) {
            return ResponseEntity.status(e.getStatusCode()).body(e.getResponseBodyAsString());
        } catch (Exception e) {
            // Handle other crashes (like Connection Refused)
            return ResponseEntity.internalServerError().body("Login failed: " + e.getMessage());
        }
    }

}
