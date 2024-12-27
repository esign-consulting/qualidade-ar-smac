package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.*;

import java.io.IOException;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Controller {

    @GetMapping("/boletim")
    public ResponseEntity<Boletim> listarMedicoes(@RequestParam(required = false) String data) throws IOException, InterruptedException {
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor(data));
        EstacoesGeoJsonParser estacoesParser = new EstacoesGeoJsonParser(new EstacoesGeoJsonRequestor());
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getFeatureCollection());
        return new ResponseEntity<>(boletim, HttpStatus.OK);
    }

    @GetMapping(value = "/prometheus", produces = MediaType.TEXT_PLAIN_VALUE)
    public String prometheusMetrics() throws IOException, InterruptedException {
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor());
        EstacoesGeoJsonParser estacoesParser = new EstacoesGeoJsonParser(new EstacoesGeoJsonRequestor());
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getFeatureCollection());
        Prometheus prometheus = new Prometheus(boletim);
        return prometheus.getMetrics();
    }

    @GetMapping(value = "/estacoes", produces = MediaType.TEXT_PLAIN_VALUE)
    public String listarEstacoes() throws IOException, InterruptedException {
        EstacoesGeoJsonRequestor reequestor = new EstacoesGeoJsonRequestor();
        return reequestor.request();
    }

}