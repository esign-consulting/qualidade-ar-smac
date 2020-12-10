package br.com.esign.qualidadearsmac;

import java.util.List;

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

}
