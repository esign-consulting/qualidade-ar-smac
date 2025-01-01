package br.com.esign.qualidadearsmac;

import java.io.IOException;

import org.geojson.FeatureCollection;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class EstacoesGeoJsonParser {

    private final FeatureCollection featureCollection;

    public EstacoesGeoJsonParser() throws IOException {
        this(new EstacoesGeoJsonRequestor());
    }

    public EstacoesGeoJsonParser(EstacoesGeoJsonRequestor requestor) throws IOException {
        this(requestor.request());
    }

    public EstacoesGeoJsonParser(String geoJson) throws JsonProcessingException {
        featureCollection = new ObjectMapper().readValue(geoJson, FeatureCollection.class);
    }

    public FeatureCollection getFeatureCollection() {
        return featureCollection;
    }

}
