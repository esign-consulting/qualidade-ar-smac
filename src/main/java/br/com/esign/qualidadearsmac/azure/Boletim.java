package br.com.esign.qualidadearsmac.azure;

import java.io.IOException;
import java.util.function.Function;

import org.springframework.stereotype.Component;

import br.com.esign.qualidadearsmac.BoletimHtmlParser;
import br.com.esign.qualidadearsmac.BoletimHtmlRequestor;
import br.com.esign.qualidadearsmac.DataRioEstacoesGeoJsonParser;
import br.com.esign.qualidadearsmac.DataRioEstacoesGeoJsonRequestor;

@Component
public class Boletim implements Function<String, br.com.esign.qualidadearsmac.model.Boletim> {

    @Override
    public br.com.esign.qualidadearsmac.model.Boletim apply(String data) {
        try {
            BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor(data));
            DataRioEstacoesGeoJsonParser estacoesParser = new DataRioEstacoesGeoJsonParser(new DataRioEstacoesGeoJsonRequestor());
            return boletimParser.obterBoletim(estacoesParser.getDataRioEstacoesFeatureCollection());
        } catch (IOException e) {
            throw new RuntimeException("Failed to process Boletim due to an IO error", e);
        }
    }

}
