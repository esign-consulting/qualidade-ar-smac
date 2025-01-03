package br.com.esign.qualidadearsmac;

import java.io.IOException;

import org.geojson.FeatureCollection;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class DataRioEstacoesGeoJsonParser {

    private final FeatureCollection dataRioEstacoesFeatureCollection;

    public DataRioEstacoesGeoJsonParser() throws IOException {
        this(new DataRioEstacoesGeoJsonRequestor());
    }

    public DataRioEstacoesGeoJsonParser(DataRioEstacoesGeoJsonRequestor requestor) throws IOException {
        this(requestor.request());
    }

    public DataRioEstacoesGeoJsonParser(String dataRioEstacoesGeoJson) throws JsonProcessingException {
        dataRioEstacoesFeatureCollection = new ObjectMapper().readValue(dataRioEstacoesGeoJson, FeatureCollection.class);
    }

    public FeatureCollection getDataRioEstacoesFeatureCollection() {
        return dataRioEstacoesFeatureCollection;
    }

}
