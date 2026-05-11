package com.project.gateway.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import org.springframework.http.HttpMethod;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;


@Configuration
public class GatewayConfig {

    @Value("${cors.allowed-origins:http://localhost:3000}")
    private String allowedOrigins;

    @Bean
    public RouteLocator routes(RouteLocatorBuilder builder) {
        return builder.routes()
                .route("login-rewrite", r -> r.path("/login")
                        .and().method(HttpMethod.POST)
                        .filters(f -> f.rewritePath("/login", "/oauth2/token"))
                        .uri("lb://authorization-service"))
                .route("authorization-service", r -> r.path("/api/authen/**")
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
        CorsConfiguration corsConfig = new CorsConfiguration();

        List<String> origins = Arrays.stream(allowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
        corsConfig.setAllowedOrigins(origins);
        corsConfig.setAllowCredentials(true);

        //llow HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
        corsConfig.setMaxAge(3600L);
        corsConfig.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        corsConfig.addAllowedHeader("*");
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }
}
