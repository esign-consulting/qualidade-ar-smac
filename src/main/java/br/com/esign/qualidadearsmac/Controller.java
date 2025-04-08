package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.*;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.fasterxml.jackson.databind.JsonNode;

@RestController
public class Controller {

    @GetMapping(value = "/boletim", produces = "application/json;charset=UTF-8")
    public ResponseEntity<Boletim> obterBoletim(@RequestParam(required = false) String data) throws IOException {
        if (data != null && !data.isEmpty()) {
            try {
                DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy");
                LocalDate initialDate = LocalDate.parse("02/08/2016", formatter);
                LocalDate dataBoletim = LocalDate.parse(data, formatter);
                if (dataBoletim.isBefore(initialDate)) {
                    throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Boletim não encontrado. A data do boletim deve ser posterior a 01/08/2016.");
                }
            } catch (DateTimeParseException e) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Data inválida. O formato da data deve ser DD/MM/AAAA.");
            }
        }
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

    @GetMapping(value = "/monitorar/ultimas24h", produces = MediaType.TEXT_PLAIN_VALUE)
    public String listarMonitorArUltimas24h() throws IOException {
        MonitorArEstacoesJsonParser estacoesParser = new MonitorArEstacoesJsonParser(new MonitorArEstacoesJsonRequestor());
        JsonNode monitorArEstacoesJsonNode = estacoesParser.getMonitorArEstacoesJsonNode();
        MonitorArUltimas24hRequestor ultimas24hRequestor = new MonitorArUltimas24hRequestor(monitorArEstacoesJsonNode);
        return ultimas24hRequestor.request();
    }

}