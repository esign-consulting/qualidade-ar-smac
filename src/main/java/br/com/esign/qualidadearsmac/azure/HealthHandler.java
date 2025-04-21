package br.com.esign.qualidadearsmac.azure;

import java.util.Optional;

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
public class HealthHandler {

    @FunctionName("health")
    public HttpResponseMessage handleRequest(
        @HttpTrigger(
            name = "req",
            methods = { HttpMethod.GET, HttpMethod.HEAD },
            authLevel = AuthorizationLevel.ANONYMOUS)
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {
        final String jsonDocument = "{\"status\":\"UP\"}";
        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body(jsonDocument)
                .build();
    }

}
