package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.Boletim;
import br.com.esign.qualidadearsmac.model.Medicao;

import java.io.IOException;
import java.nio.file.Files;
import java.util.Optional;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import static org.assertj.core.api.Assertions.assertThat;

@ContextConfiguration(classes = Application.class)
@RunWith(SpringRunner.class)
@SpringBootTest
public class BoletimHtmlParserTest {

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void obterBoletimTest() throws IOException {
        Resource boletimResource = resourceLoader.getResource("classpath:boletim.html");
        String boletimHtml = new String(Files.readAllBytes(boletimResource.getFile().toPath()));
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(boletimHtml);
        Resource dataRioEstacoesResource = resourceLoader.getResource("classpath:datario-estacoes.json");
        String dataRioEstacoesGeoJson = new String(Files.readAllBytes(dataRioEstacoesResource.getFile().toPath()));
        DataRioEstacoesGeoJsonParser estacoesParser = new DataRioEstacoesGeoJsonParser(dataRioEstacoesGeoJson);
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getDataRioEstacoesFeatureCollection());
        assertThat(boletim.getData()).isEqualTo("26/12/2024");
        assertThat(boletim.getMedicoes().stream().filter(m -> m.getEstacao().getNome().equals("Campo Grande")).findFirst()).isPresent();
        
        Optional<Medicao> optional = boletim.getMedicoes().stream().filter(m -> m.getEstacao().getNome().equals("Pedra de Guaratiba")).findFirst();
        assertThat(optional).isPresent();
        Medicao medicao = optional.get();
        assertThat(medicao.getEstacao().getLatitude()).isEqualTo(-23.0043789751932);
        assertThat(medicao.getEstacao().getLongitude()).isEqualTo(-43.629010366464);
    }

}
