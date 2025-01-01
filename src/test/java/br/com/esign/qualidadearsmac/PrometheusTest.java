package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.nio.file.Files;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import br.com.esign.qualidadearsmac.model.Boletim;

import static org.assertj.core.api.Assertions.assertThat;

@ContextConfiguration(classes = Application.class)
@RunWith(SpringRunner.class)
@SpringBootTest
public class PrometheusTest {

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void listMetricsTest() throws IOException {
        Resource boletimResource = resourceLoader.getResource("classpath:boletim.html");
        String html = new String(Files.readAllBytes(boletimResource.getFile().toPath()));
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(html);
        Resource estacoesResource = resourceLoader.getResource("classpath:estacoes.json");
        String geoJson = new String(Files.readAllBytes(estacoesResource.getFile().toPath()));
        EstacoesGeoJsonParser estacoesParser = new EstacoesGeoJsonParser(geoJson);
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getFeatureCollection());
        Prometheus prometheus = new Prometheus(boletim);
        String metrics = prometheus.getMetrics();
        assertThat(metrics).contains("iqar{estado=\"RJ\",cidade=\"Rio de Janeiro\",orgao=\"SMAC\",estacao=\"Tijuca\",poluente=\"Material Particulado (MP10)\",classificacao=\"Boa\"} 20 1735171200000");
    }

}
