package com.project.gateway.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import org.springframework.http.HttpMethod;
import org.springframework.web.cors.CorsConfiguration; //CORS rules (origins, methods, headers, credentials)
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;


@Configuration
public class GatewayConfig {

    //allowed origins for browser requests (can be comma-separated in application.yml)
    @Value("${cors.allowed-origins:http://localhost:3000}")
    private String allowedOrigins;

    @Bean
    public RouteLocator routes(RouteLocatorBuilder builder) {
        //Spring Cloud Gateway routes: map external paths to internal services through discovery (lb://)
        return builder.routes()
                .route("login-rewrite", r -> r.path("/login")
                        .and().method(HttpMethod.POST)
                        //frontend posts to /login, but authorization-server expects /oauth2/token
                        .filters(f -> f.rewritePath("/login", "/oauth2/token"))
                        .uri("lb://authorization-service")) //forward to authorization-service
                .route("authorization-service", r -> r.path("/api/authen/**")
                        //stripPrefix(2) turns /api/authen/... into /... before sending to the service
                        .filters(f -> f.stripPrefix(2))
                        .uri("lb://authorization-service"))
                .route("user-service", r -> r.path("/api/user/**")
                        .filters(f -> f.stripPrefix(2))
                        .uri("lb://user-service"))
                .route("personalization-service", r -> r.path("/api/personalization/**")
                        .filters(f -> f.stripPrefix(2))
                        .uri("lb://personalization-service"))
                .route("chat-service", r -> r.path("/api/chat/**")
                        .filters(f -> f.stripPrefix(2))
                        .uri("lb://chat-service"))
                .build();
    }

    @Bean
    public CorsWebFilter corsWebFilter() {
        //CORS is needed so the frontend (different port/domain) can call the gateway APIs
        CorsConfiguration corsConfig = new CorsConfiguration(); //holds all CORS settings

        //support multiple allowed origins by splitting comma-separated config
        List<String> origins = Arrays.stream(allowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
        corsConfig.setAllowedOrigins(origins); //exact origin list (important when credentials=true)
        corsConfig.setAllowCredentials(true); //allow cookies/Authorization headers if your app uses them

        //allow HTTP methods used by the UI + preflight OPTIONS
        corsConfig.setMaxAge(3600L); //cache preflight response for 1 hour
        corsConfig.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS")); //allowed verbs
        corsConfig.addAllowedHeader("*"); //allow any header (Content-Type, Authorization, etc.)
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource(); //bind rules to URL patterns
        source.registerCorsConfiguration("/**", corsConfig); //apply to every route

        return new CorsWebFilter(source); //reactive filter used by Spring Cloud Gateway
    }
}
