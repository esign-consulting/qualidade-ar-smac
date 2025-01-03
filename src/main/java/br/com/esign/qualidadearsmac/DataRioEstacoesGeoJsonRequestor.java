package br.com.esign.qualidadearsmac;

import java.io.IOException;

public class DataRioEstacoesGeoJsonRequestor extends Requestor {

    public static final String URL_DATARIO_ESTACOES = "https://hub.arcgis.com/api/v3/datasets/5b1bf5c3e5114564bbf9b7a372b85e17_0/downloads/data?format=geojson&spatialRefId=4326";

    private String url;

    public DataRioEstacoesGeoJsonRequestor() {
        this(URL_DATARIO_ESTACOES);
    }

     public DataRioEstacoesGeoJsonRequestor(String url) {
        this.url = url;
    }

    public String request() throws IOException {
        return request(url);
    }

}
