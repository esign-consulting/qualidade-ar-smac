package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.util.List;

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
    public ResponseEntity<List<Medicao>> listarMedicoes(@RequestParam(required = false) String data) throws IOException, InterruptedException {
        BoletimDiario boletimDiario = new BoletimDiario(new HtmlRequestor(data));
        List<Medicao> medicoes = boletimDiario.listarMedicoes();
        return new ResponseEntity<>(medicoes, HttpStatus.OK);
    }

    @GetMapping(value = "/prometheus", produces = MediaType.TEXT_PLAIN_VALUE)
    @ResponseBody
    public String prometheusMetrics() throws IOException, InterruptedException {
        BoletimDiario boletimDiario = new BoletimDiario(new HtmlRequestor());
        List<Medicao> medicoes = boletimDiario.listarMedicoes();
        Prometheus prometheus = new Prometheus(medicoes);
        return prometheus.getMetrics();
    }

}