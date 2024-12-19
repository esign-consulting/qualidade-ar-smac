FROM maven:3.9.9-eclipse-temurin-22-alpine AS builder
WORKDIR /qualidadearsmac
COPY pom.xml .
COPY src ./src
RUN mvn install

FROM eclipse-temurin:22-alpine
COPY --from=builder /qualidadearsmac/target/qualidadearsmac-0.0.1-SNAPSHOT.jar ./
EXPOSE 8080
CMD ["java", "-jar", "qualidadearsmac-0.0.1-SNAPSHOT.jar"]