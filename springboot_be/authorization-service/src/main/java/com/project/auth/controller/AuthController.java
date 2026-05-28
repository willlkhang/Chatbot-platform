package com.project.auth.controller;

import com.project.base.loginDto.LoginRequest; //simple login payload (username/password) from client
import org.springframework.beans.factory.annotation.Value; //inject values from application.yml
import org.springframework.http.*; //ResponseEntity + HttpHeaders + MediaType + HttpEntity
import org.springframework.util.LinkedMultiValueMap; //form-url-encoded body builder
import org.springframework.util.MultiValueMap; //spring representation for key=value form fields
import org.springframework.web.bind.annotation.GetMapping; //maps GET endpoints
import org.springframework.web.bind.annotation.PostMapping; //maps POST endpoints
import org.springframework.web.bind.annotation.RequestBody; //bind JSON body to DTO
import org.springframework.web.bind.annotation.RestController; //marks this class as REST controller
import org.springframework.web.client.HttpClientErrorException; //catch 4xx from OAuth server
import org.springframework.web.client.RestTemplate; //simple HTTP client for proxying token requests

import java.util.Map;

@RestController
public class AuthController {

    private final RestTemplate restTemplate = new RestTemplate(); //used to call the internal OAuth token endpoint

    @Value("${spring.profiles.active}")
    private String whoami; //active profile string (used by /test endpoint)

    @Value("${spring.app.oauth-url}")
    private String oauthTokenUrl; //token endpoint URL (usually points at /oauth2/token)

    @Value("${spring.security.oauth2.resourceserver.jwt.client-id:project}")
    private String clientId; //client id for basic auth when calling token endpoint

    @Value("${spring.security.oauth2.resourceserver.jwt.client-secret:secret}")
    private String clientSecret; //client secret for basic auth when calling token endpoint

    @GetMapping("/test")
    public ResponseEntity<?> test(){
        return ResponseEntity.ok(whoami); //simple test to confirm config/profile is loaded
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        String url = this.oauthTokenUrl; //target token endpoint

        //prepare request exactly like Postman: form body + Basic Auth(client_id, client_secret)
        HttpHeaders headers = new HttpHeaders(); //http headers
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED); //OAuth expects form fields (not JSON)
        headers.setBasicAuth(clientId, clientSecret); //client credentials used by authorization server

        MultiValueMap<String, String> body = new LinkedMultiValueMap<>(); //form fields for token endpoint
        body.add("grant_type", "password"); //password grant (your auth server supports this custom flow)
        body.add("username", request.getUsername()); //user credentials from client
        body.add("password", request.getPassword()); //user credentials from client

        HttpEntity<MultiValueMap<String, String>> entity = new HttpEntity<>(body, headers); //combine headers + form body

        try {
            // "Map.class" is a generic way to catch whatever JSON comes back (access_token, etc.)
            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    Map.class
            );
            return ResponseEntity.ok(response.getBody()); //return token payload back to frontend
        } catch (HttpClientErrorException e) {
            //when OAuth server returns 4xx (invalid_grant, invalid_client, etc.), forward the body
            return ResponseEntity.status(e.getStatusCode()).body(e.getResponseBodyAsString());
        } catch (Exception e) {
            // Handle other crashes (like Connection Refused)
            return ResponseEntity.internalServerError().body("Login failed: " + e.getMessage());
        }
    }

}
