package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.*;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class Prometheus {
    
    private final Boletim boletim;

    public Prometheus(Boletim boletim) {
        this.boletim = boletim;
    }

    public String getMetrics() {
        return getIQAr();
    }

    private String getIQAr() {
        String newLine = System.getProperty("line.separator");
        SimpleDateFormat parser = new SimpleDateFormat("dd/MM/yyyy");
        Date timestamp = null;
        try {
            timestamp = parser.parse(boletim.getData());
        } catch (ParseException e) {
            throw new RuntimeException("Erro na obtenção da data da medição da qualidade do ar.");
        }
        List<String> iqarLines = new ArrayList<>();
        iqarLines.add("# HELP iqar Índice de Qualidade do Ar");
        iqarLines.add("# TYPE iqar gauge");
        for (Medicao medicao : boletim.getMedicoes()) {
            iqarLines.add(String.format("iqar{estado=\"%s\",cidade=\"%s\",orgao=\"%s\",estacao=\"%s\",poluente=\"%s\",classificacao=\"%s\"} %s %tQ",
                "RJ",
                "Rio de Janeiro",
                "SMAC",
                medicao.getEstacao().getNome(),
                medicao.getPoluente(),
                medicao.getClassificacao(),
                medicao.getIndice(),
                timestamp));
        }
        return String.join(newLine, iqarLines);
    }

}
