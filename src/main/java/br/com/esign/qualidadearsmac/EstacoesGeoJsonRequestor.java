package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class EstacoesGeoJsonRequestor {

    public static final String URL_ESTACOES = "https://hub.arcgis.com/api/v3/datasets/5b1bf5c3e5114564bbf9b7a372b85e17_0/downloads/data?format=geojson&spatialRefId=4326";

    private String url;

    public EstacoesGeoJsonRequestor() {
        this(URL_ESTACOES);
    }

     public EstacoesGeoJsonRequestor(String url) {
        this.url = url;
    }

    public String request() throws IOException, InterruptedException {
        try (HttpClient client = HttpClient.newHttpClient()) {
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create(url)).build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            return response.body();
        }
    }

}
