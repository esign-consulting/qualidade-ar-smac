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

    private Boletim boletim;

    @Autowired
    public BoletimHandler(Boletim boletim) {
        this.boletim = boletim;
    }

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
                if (dataBoletim.isBefore(initialDate))
                    return createErrorResponseMessage(request, HttpStatus.NOT_FOUND,
                        "Boletim não encontrado. A data do boletim deve ser posterior a 01/08/2016.");
            } catch (DateTimeParseException e) {
                return createErrorResponseMessage(request, HttpStatus.BAD_REQUEST,
                    "Data inválida. O formato da data deve ser DD/MM/AAAA.");
            }
        }
        try {
            return createSuccessResponseMessage(request, boletim.apply(data));
        } catch (Exception e) {
            context.getLogger().severe("Error processing request: " + e.getMessage());
            return createErrorResponseMessage(request, HttpStatus.INTERNAL_SERVER_ERROR,
                    "Error processing request: " + e.getMessage());
        }
    }

    private HttpResponseMessage createErrorResponseMessage(HttpRequestMessage<Optional<String>> request, HttpStatus status, String message) {
        return request.createResponseBuilder(status)
                .body(message)
                .header("Content-Type", "text/plain")
                .build();
    }

    private HttpResponseMessage createSuccessResponseMessage(HttpRequestMessage<Optional<String>> request, br.com.esign.qualidadearsmac.model.Boletim boletim) {
        return request.createResponseBuilder(HttpStatus.OK)
                .body(boletim)
                .header("Content-Type", "application/json")
                .build();
    }

}
