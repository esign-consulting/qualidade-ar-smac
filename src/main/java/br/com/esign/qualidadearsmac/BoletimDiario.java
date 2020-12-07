package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

    private Date obterDatahoraMedicao() {
        Date datahoraMedicao = null;
        String regex = "(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\\d\\d)";
        Pattern pattern = Pattern.compile(regex);
        Element div = doc.getElementById("titulo");
        Matcher matcher = pattern.matcher(div.html());
        if (matcher.find()) {
            SimpleDateFormat parser = new SimpleDateFormat("dd/MM/yyyy");
            try {
                datahoraMedicao = parser.parse(matcher.group());
            } catch (ParseException e) {
                throw new RuntimeException("Erro na obtenção da data/hora da medição da qualidade do ar.");
            }
        }
        return datahoraMedicao;
    }

    public List<Medicao> listarMedicoes() {
        Date datahora = obterDatahoraMedicao();
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
                    medicao.setDatahora(datahora);
                    medicao.setEstacao(tds.get(0).text());
                    for (int k = 0, l = 1; k < size; k++, l++) {
                        if (tds.get(l).attr("class").equals("td_value_bold")) {
                            medicao.setPoluente(poluentes.get(k));
                            break;
                        }
                    }
                    medicao.setIndice(tds.get(size + 1).text());
                    medicao.setQualidadeAr(tds.get(size + 2).text());
                    listaMedicoes.add(medicao);
                }
            }
        }
        return listaMedicoes;
    }

}
