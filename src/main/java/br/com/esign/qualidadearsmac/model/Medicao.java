package br.com.esign.qualidadearsmac.model;

import java.util.List;

public class Medicao {
    
    private Estacao estacao;
    private String classificacao;
    private String indice;
    private String poluente;
    private List<MedicaoPoluente> medicaoPoluentes;

    public Estacao getEstacao() {
        return estacao;
    }

    public void setEstacao(Estacao estacao) {
        this.estacao = estacao;
    }

    public String getClassificacao() {
        return classificacao;
    }

    public void setClassificacao(String classificacao) {
        this.classificacao = classificacao;
    }

    public String getIndice() {
        return indice;
    }

    public void setIndice(String indice) {
        this.indice = indice;
    }

    public String getPoluente() {
        return poluente;
    }

    public void setPoluente(String poluente) {
        this.poluente = poluente;
    }

    public List<MedicaoPoluente> getMedicaoPoluentes() {
        return medicaoPoluentes;
    }

    public void setMedicaoPoluentes(List<MedicaoPoluente> medicaoPoluentes) {
        this.medicaoPoluentes = medicaoPoluentes;
    }

}
