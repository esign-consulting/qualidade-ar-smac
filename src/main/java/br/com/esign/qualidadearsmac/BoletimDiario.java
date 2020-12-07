package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import org.springframework.stereotype.Component;

@Component
public class BoletimDiario {
    
    private final Document doc;

    public BoletimDiario() throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("http://jeap.rio.rj.gov.br/je-metinfosmac/boletim"))
            .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        doc = Jsoup.parse(response.body());
    }

    private String obterDataMedicao() {
        Element div = doc.getElementById("titulo");
        Elements h4s = div.getElementsByTag("h4");
        Element h4 = h4s.first();
        return (h4 == null) ? null : h4.html();
    }

    public List<Medicao> listarMedicoes() {
        String data = obterDataMedicao();
        List<Medicao> listaMedicoes = new ArrayList<>();
        Element div = doc.getElementById("dados_estacoes");
        Elements trs = div.getElementsByTag("tr");
        List<String> poluentes = new ArrayList<>();
        int size = 0;
        for (int i = 1, j = trs.size(); i < j; i++) {
            Element tr = trs.get(i);
            if (i == 1) {
                Elements ths = tr.getElementsByTag("th");
                ths.stream().forEach((th) -> {
                    poluentes.add(th.text());
                });
                size = poluentes.size();
            } else {
                Elements tds = tr.getElementsByTag("td");
                if (tds.size() == size + 3) {
                    Medicao medicao = new Medicao();
                    medicao.setData(data);
                    medicao.setEstacao(tds.get(0).text());
                    List<MedicaoPoluente> medicaoPoluentes = new ArrayList<>();
                    String poluentePrincipal = null;
                    for (int k = 0, l = 1; k < size; k++, l++) {
                        Element td = tds.get(l);
                        MedicaoPoluente medicaoPoluente = new MedicaoPoluente();
                        medicaoPoluente.setPoluente(poluentes.get(k));
                        medicaoPoluente.setConcentracao(td.text());
                        medicaoPoluentes.add(medicaoPoluente);
                        if (td.attr("class").equals("td_value_bold")) {
                            poluentePrincipal = poluentes.get(k);
                        }
                    }
                    medicao.setPoluente(poluentePrincipal);
                    medicao.setMedicaoPoluentes(medicaoPoluentes);
                    medicao.setIndice(tds.get(size + 1).text());
                    medicao.setQualidadeAr(tds.get(size + 2).text());
                    listaMedicoes.add(medicao);
                }
            }
        }
        return listaMedicoes;
    }

}
