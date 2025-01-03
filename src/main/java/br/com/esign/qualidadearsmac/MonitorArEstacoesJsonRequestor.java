package br.com.esign.qualidadearsmac;

import java.io.IOException;

public class MonitorArEstacoesJsonRequestor extends Requestor {

    public static final String URL_MONITORAR_ESTACOES = "https://monitorar-backend.mma.gov.br/v1/estacao/todas";

    private String url;

    public MonitorArEstacoesJsonRequestor() {
        this(URL_MONITORAR_ESTACOES);
    }

     public MonitorArEstacoesJsonRequestor(String url) {
        this.url = url;
    }

    public String request() throws IOException {
        return request(url);
    }

}
