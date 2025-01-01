package br.com.esign.qualidadearsmac;

import java.io.IOException;

public class BoletimHtmlRequestor extends Requestor {

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

    public String request() throws IOException {
        return request((data == null) ? url : url.concat(String.format("?data=%s", data)));
    }

}
