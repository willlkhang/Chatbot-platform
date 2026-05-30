Author: Minh Khang Nguyen
Date: 03/04/2026

## Introduction

This repository is a university project that combines:

- a **Next.js frontend** (UI)
- a **Spring Boot microservices backend** (`springboot_be`) for authentication and data services
- supporting AI services (e.g. `ragbot`, `classifier_app`) that the UI can call via HTTP

## Purpose

The goal of this project is to provide a working full-stack system where:

- users can **register/login** (OAuth2 token issued by the authorization service)
- the frontend talks to a **single backend entrypoint** (API Gateway) that routes requests to internal services
- business services (user/chat/personalization) persist data to **Postgres**
- AI components can be run alongside the backend to power chat/classification features

