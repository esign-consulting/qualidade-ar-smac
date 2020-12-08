package br.com.esign.qualidadearsmac;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

public class Prometheus {
    
    private final List<Medicao> medicoes;

    public Prometheus(List<Medicao> medicoes) {
        this.medicoes = medicoes;
    }

    public String getMetrics() {
        return getIQAr();
    }

    private String getIQAr() {
        String newLine = System.getProperty("line.separator");
        List<String> iqarLines = new ArrayList<>();
        iqarLines.add("# HELP iqar Índice de Qualidade do Ar");
        iqarLines.add("# TYPE iqar gauge");
        for (Medicao medicao : medicoes) {
            SimpleDateFormat parser = new SimpleDateFormat("dd/MM/yyyy");
            try {
                iqarLines.add(String.format("iqar{estado=\"%s\",cidade=\"%s\",orgao=\"%s\",estacao=\"%s\",poluente=\"%s\",classificacao=\"%s\"} %s %tQ",
                "RJ",
                "Rio de Janeiro",
                "SMAC",
                medicao.getEstacao(),
                medicao.getPoluente(),
                medicao.getClassificacao(),
                medicao.getIndice(),
                parser.parse(medicao.getData())));
            } catch (ParseException e) {
                throw new RuntimeException("Erro na obtenção da data da medição da qualidade do ar.");
            }
            
        }
        return String.join(newLine, iqarLines);
    }

}
