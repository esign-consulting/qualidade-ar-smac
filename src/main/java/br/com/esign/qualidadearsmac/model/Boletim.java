package br.com.esign.qualidadearsmac.model;

import java.util.List;
import com.fasterxml.jackson.annotation.JsonIgnore;

public class Boletim {

    private String data;
    private List<Medicao> medicoes;

    public String getData() {
        return data;
    }

    public void setData(String data) {
        this.data = data;
    }

    public List<Medicao> getMedicoes() {
        return medicoes;
    }

    public void setMedicoes(List<Medicao> medicoes) {
        this.medicoes = medicoes;
    }

    @JsonIgnore
    public List<Estacao> getEstacoes() {
        return this.medicoes.stream().map(Medicao::getEstacao).toList();
    }

}
