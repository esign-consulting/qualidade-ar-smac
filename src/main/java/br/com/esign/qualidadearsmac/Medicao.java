package br.com.esign.qualidadearsmac;

import java.util.Date;
import java.util.List;

public class Medicao {
    
    private Date datahora;
    private String estacao;
    private String qualidadeAr;
    private String indice;
    private String poluente;
    private List<MedicaoPoluente> medicaoPoluentes;

    public Date getDatahora() {
        return datahora;
    }

    public void setDatahora(Date datahora) {
        this.datahora = datahora;
    }

    public String getEstacao() {
        return estacao;
    }

    public void setEstacao(String estacao) {
        this.estacao = estacao;
    }

    public String getQualidadeAr() {
        return qualidadeAr;
    }

    public void setQualidadeAr(String qualidadeAr) {
        this.qualidadeAr = qualidadeAr;
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
