package br.com.esign.qualidadearsmac.azure;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.HttpMethod;
import com.microsoft.azure.functions.HttpRequestMessage;
import com.microsoft.azure.functions.HttpResponseMessage;
import com.microsoft.azure.functions.HttpStatus;
import com.microsoft.azure.functions.annotation.AuthorizationLevel;
import com.microsoft.azure.functions.annotation.FunctionName;
import com.microsoft.azure.functions.annotation.HttpTrigger;

@Component
public class BoletimHandler {

    @Autowired
    private Boletim boletim;

    @FunctionName("boletim")
    public HttpResponseMessage handleRequest(
        @HttpTrigger(
            name = "req",
            methods = { HttpMethod.GET },
            authLevel = AuthorizationLevel.ANONYMOUS)
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {
        context.getLogger().info("Java HTTP trigger processed a request.");
        String data = request.getQueryParameters().get("data");
        context.getLogger().info("Data received: " + data);
        if (data != null && !data.isEmpty()) {
            try {
                DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy");
                LocalDate initialDate = LocalDate.parse("02/08/2016", formatter);
                LocalDate dataBoletim = LocalDate.parse(data, formatter);
                if (dataBoletim.isBefore(initialDate)) {
                    return request.createResponseBuilder(HttpStatus.NOT_FOUND)
                            .body("Boletim não encontrado. A data do boletim deve ser posterior a 01/08/2016.")
                            .header("Content-Type", "text/plain")
                            .build();
                }
            } catch (DateTimeParseException e) {
                return request.createResponseBuilder(HttpStatus.BAD_REQUEST)
                        .body("Data inválida. O formato da data deve ser DD/MM/AAAA.")
                        .header("Content-Type", "text/plain")
                        .build();
            }
        }
        try {
            return request.createResponseBuilder(HttpStatus.OK)
                    .body(boletim.apply(data))
                    .header("Content-Type", "application/json")
                    .build();
        } catch (Exception e) {
            context.getLogger().severe("Error processing request: " + e.getMessage());
            e.printStackTrace();
            return request.createResponseBuilder(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error processing request: " + e.getMessage())
                    .header("Content-Type", "text/plain")
                    .build();
        }
    }

}
