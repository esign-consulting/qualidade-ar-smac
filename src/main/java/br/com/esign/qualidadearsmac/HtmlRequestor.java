package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;

public class HtmlRequestor {

    public static final String URL_BOLETIM = "http://jeap.rio.rj.gov.br/je-metinfosmac/boletim";

    public String request() throws IOException, InterruptedException {
        return request(URL_BOLETIM);
    }

    public String request(String url) throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder().uri(URI.create(url)).build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

}
