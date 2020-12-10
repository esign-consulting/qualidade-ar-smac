package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;

public class BoletimHtmlRequestor {

    public static final String URL_BOLETIM = "http://jeap.rio.rj.gov.br/je-metinfosmac/boletim";

    private String url;
    private String data;

    public BoletimHtmlRequestor() {
        this(URL_BOLETIM, null);
    }

    public BoletimHtmlRequestor(String data) {
        this(URL_BOLETIM, data);
    }

    public BoletimHtmlRequestor(String url, String data) {
        this.url = url;
        this.data = data;
    }

    public String request() throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder().uri(URI.create((data == null) ? url : url.concat(String.format("?data=%s", data)))).build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

}
