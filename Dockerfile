FROM maven:3.6.3-openjdk-11-slim AS builder
WORKDIR /qualidadearsmac
COPY pom.xml .
COPY src ./src
RUN mvn install

FROM openjdk:11-jre-slim-buster
COPY --from=builder /qualidadearsmac/target/qualidadearsmac-0.0.1-SNAPSHOT.jar ./
EXPOSE 8080
CMD ["java", "-jar", "qualidadearsmac-0.0.1-SNAPSHOT.jar"]