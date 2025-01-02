package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.*;

import java.io.IOException;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.databind.JsonNode;

@RestController
public class Controller {

    @GetMapping(value = "/boletim", produces = "application/json;charset=UTF-8")
    public ResponseEntity<Boletim> listarMedicoes(@RequestParam(required = false) String data) throws IOException {
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor(data));
        EstacoesGeoJsonParser estacoesParser = new EstacoesGeoJsonParser(new EstacoesGeoJsonRequestor());
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getFeatureCollection());
        return new ResponseEntity<>(boletim, HttpStatus.OK);
    }

    @GetMapping(value = "/prometheus", produces = MediaType.TEXT_PLAIN_VALUE)
    public String prometheusMetrics() throws IOException {
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor());
        EstacoesGeoJsonParser estacoesParser = new EstacoesGeoJsonParser(new EstacoesGeoJsonRequestor());
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getFeatureCollection());
        Prometheus prometheus = new Prometheus(boletim);
        return prometheus.getMetrics();
    }

    @GetMapping(value = "/estacoes", produces = MediaType.TEXT_PLAIN_VALUE)
    public String listarEstacoes() throws IOException {
        EstacoesGeoJsonRequestor reequestor = new EstacoesGeoJsonRequestor();
        return reequestor.request();
    }

    @GetMapping(value = "/monitorar/estacoes", produces = "application/json;charset=UTF-8")
    public ResponseEntity<JsonNode> listarMonitorArEstacoes() throws IOException {
        MonitorArEstacoesJsonParser estacoesParser = new MonitorArEstacoesJsonParser(new MonitorArEstacoesJsonRequestor());
        JsonNode jsonNode = estacoesParser.getJsonNode();
        return new ResponseEntity<>(jsonNode, HttpStatus.OK);
    }

}