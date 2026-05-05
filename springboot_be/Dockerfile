FROM maven:3.9.9-eclipse-temurin-23 AS build

WORKDIR /workspace
#module to build which is the services
ARG SERVICE

#copy POM files to leverage docker layer
COPY pom.xml ./pom.xml
COPY authorization-service/pom.xml ./authorization-service/pom.xml
COPY base-service/pom.xml ./base-service/pom.xml
COPY chat-service/pom.xml ./chat-service/pom.xml
COPY config-service/pom.xml ./config-service/pom.xml
COPY discovery-service/pom.xml ./discovery-service/pom.xml
COPY gateway-service/pom.xml ./gateway-service/pom.xml
COPY personalization-service/pom.xml ./personalization-service/pom.xml
COPY user-service/pom.xml ./user-service/pom.xml

#download dependencies
RUN --mount=type=cache,target=/root/.m2 \
    mvn -DskipTests dependency:go-offline

#copy full mnodules source
COPY . .


#build only request services or modules
#this way helps me not to run mvn then docker, but, combine them
RUN test -n "$SERVICE"
RUN --mount=type=cache,target=/root/.m2 \
    mvn -DskipTests -pl "${SERVICE}" -am package


FROM amazoncorretto:23-alpine AS runtime
WORKDIR /app

ARG SERVICE
COPY --from=build /workspace/${SERVICE}/target/*.jar /app/app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]

