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
    public ResponseEntity<Boletim> obterBoletim(@RequestParam(required = false) String data) throws IOException {
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor(data));
        DataRioEstacoesGeoJsonParser estacoesParser = new DataRioEstacoesGeoJsonParser(new DataRioEstacoesGeoJsonRequestor());
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getDataRioEstacoesFeatureCollection());
        return new ResponseEntity<>(boletim, HttpStatus.OK);
    }

    @GetMapping(value = "/prometheus", produces = MediaType.TEXT_PLAIN_VALUE)
    public String prometheusMetrics() throws IOException {
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(new BoletimHtmlRequestor());
        DataRioEstacoesGeoJsonParser estacoesParser = new DataRioEstacoesGeoJsonParser(new DataRioEstacoesGeoJsonRequestor());
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getDataRioEstacoesFeatureCollection());
        Prometheus prometheus = new Prometheus(boletim);
        return prometheus.getMetrics();
    }

    @GetMapping(value = "/datario/estacoes", produces = MediaType.TEXT_PLAIN_VALUE)
    public String listarDataRioEstacoes() throws IOException {
        DataRioEstacoesGeoJsonRequestor dataRioEstacoesRequestor = new DataRioEstacoesGeoJsonRequestor();
        return dataRioEstacoesRequestor.request();
    }

    @GetMapping(value = "/monitorar/estacoes", produces = "application/json;charset=UTF-8")
    public ResponseEntity<JsonNode> listarMonitorArEstacoes() throws IOException {
        MonitorArEstacoesJsonParser estacoesParser = new MonitorArEstacoesJsonParser(new MonitorArEstacoesJsonRequestor());
        JsonNode monitorArEstacoesJsonNode = estacoesParser.getMonitorArEstacoesJsonNode();
        return new ResponseEntity<>(monitorArEstacoesJsonNode, HttpStatus.OK);
    }

    @GetMapping(value = "/monitorar/dados-horarios", produces = MediaType.TEXT_PLAIN_VALUE)
    public String listarMonitorArDadosHorarios() throws IOException {
        MonitorArEstacoesJsonParser estacoesParser = new MonitorArEstacoesJsonParser(new MonitorArEstacoesJsonRequestor());
        JsonNode monitorArEstacoesJsonNode = estacoesParser.getMonitorArEstacoesJsonNode();
        MonitorArDadosHorariosRequestor dadosHorariosRequestor = new MonitorArDadosHorariosRequestor(monitorArEstacoesJsonNode);
        return dadosHorariosRequestor.request();
    }

}