package br.com.esign.qualidadearsmac;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/boletim")
public class Controller {

    @Autowired
    private BoletimDiario boletimDiario;

    @GetMapping("/medicoes")
    @ResponseBody
    public ResponseEntity<List<Medicao>> listarMedicoes() {
        List<Medicao> medicoes = boletimDiario.listarMedicoes();
        return new ResponseEntity<>(medicoes, HttpStatus.OK);
    }

}