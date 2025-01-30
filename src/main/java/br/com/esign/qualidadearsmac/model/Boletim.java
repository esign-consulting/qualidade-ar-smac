package br.com.esign.qualidadearsmac.model;

import java.util.List;
import java.util.stream.Collectors;

public class Boletim {

    private String data;
    private List<Medicao> medicoes;
    private List<Estacao> estacoes;

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

    public List<Estacao> getEstacoes() {
        return this.medicoes.stream().map(m -> m.getEstacao()).collect(Collectors.toList());
    }

}
