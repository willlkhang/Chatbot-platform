# `springboot_be` backend documentation

## Introduction

`springboot_be` is the **backend platform** for this project. It is implemented as a **Spring Boot + Spring Cloud** microservices system, packaged as a **multi-module Maven** repository.

## Purpose

The purpose of this backend is to give the frontend a consistent and scalable API layer by:

- exposing a **single entrypoint** (Spring Cloud Gateway) for all backend APIs
- handling **authentication** and **JWT issuance** via an authorization service (OAuth2 password grant)
- providing separate business services for **users**, **chat**, and **personalization**
- centralizing configuration in **Spring Cloud Config Server** (so ports/DB/issuer settings are managed in one place)
- using **Eureka discovery** so the gateway can route to services by name (`lb://service-name`)

This folder contains the Spring Boot / Spring Cloud backend implementation and documentation.

## Quick start (Docker Compose)

The main project-level `docker-compose.yml` builds and runs the backend services for you (plus Postgres).

- **Start everything** (from repo root):

```bash
docker compose up --build
```

- **Gateway is the public entrypoint**:
  - The gateway container listens on **`8060`** internally.
  - It is published to your host using `GATEWAY_HOST_PORT` in `docker-compose.yml`.

## Services overview

All services below are built from the same shared Dockerfile: `springboot_be/Dockerfile` (you pass `SERVICE=<module>` to build only one module jar).

| Service | Spring app name | Internal port | Purpose |
|---|---|---:|---|
| Config Server | `config-service` | **8088** | Serves YAML config to all services from `classpath:/config` |
| Discovery (Eureka) | `discovery-service` | **8061** | Service registry (`lb://...` resolution) |
| API Gateway | `gateway-service` | **8060** | Public entrypoint, routing + CORS |
| Authorization | `authorization-service` | **8087** | OAuth2 Authorization Server (password grant) + JWT issuer |
| User | `user-service` | **8085** | User CRUD + registration, JWT-protected |
| Chat | `chat-service` | **8086** | Chat + messages persistence, JWT-protected |
| Personalization | `personalization-service` | **8083** | Personalization persistence, DB-backed |
| Base module | `base-service` | (library) | Shared domain DTOs/entities used by other services |

## Centralized configuration

Most runtime settings (ports, datasource, issuer uri, etc.) come from **Config Server**:

- Config Server loads YAMLs from:
  - `springboot_be/config-service/src/main/resources/config/*.yml`
- Each service bootstrap file contains:
  - `spring.config.import: configserver:${CONFIG_SERVER_URL:http://localhost:8088/}`

## Main request flows (high level)

### 1) Login (OAuth token)

Client -> **Gateway** -> **Authorization Service** (OAuth2 password grant) -> returns access token (JWT).

- Client sends `POST /login` (gateway route rewrites it to `/oauth2/token` on `authorization-service`)
- Authorization Service uses custom password converter/provider to validate username/password and generate JWT.

### 2) Authenticated API calls

Client -> **Gateway** -> service (`user-service`, `chat-service`, etc.)

- Gateway routes based on path prefixes (`/api/user/**`, `/api/chat/**`, `/api/personalization/**`, `/api/authen/**`)
- Services that act as resource servers validate JWT via `issuer-uri` pointing at `authorization-service`.

## Where to read more

- **System architecture & flows**: `springboot_be/docs/architecture-and-flows.md`
- **Per-service docs**:
  - `springboot_be/docs/service-gateway.md`
  - `springboot_be/docs/service-discovery.md`
  - `springboot_be/docs/service-config.md`
  - `springboot_be/docs/service-authorization.md`
  - `springboot_be/docs/service-user.md`
  - `springboot_be/docs/service-chat.md`
  - `springboot_be/docs/service-personalization.md`

