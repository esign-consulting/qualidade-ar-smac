package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.*;

import java.io.IOException;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Controller {

    @GetMapping("/boletim")
    @ResponseBody
    public ResponseEntity<Boletim> listarMedicoes(@RequestParam(required = false) String data) throws IOException, InterruptedException {
        BoletimHtmlParser parser = new BoletimHtmlParser(new BoletimHtmlRequestor(data));
        Boletim boletim = parser.obterBoletim();
        return new ResponseEntity<>(boletim, HttpStatus.OK);
    }

    @GetMapping(value = "/prometheus", produces = MediaType.TEXT_PLAIN_VALUE)
    @ResponseBody
    public String prometheusMetrics() throws IOException, InterruptedException {
        BoletimHtmlParser parser = new BoletimHtmlParser(new BoletimHtmlRequestor());
        Boletim boletim = parser.obterBoletim();
        Prometheus prometheus = new Prometheus(boletim);
        return prometheus.getMetrics();
    }

}