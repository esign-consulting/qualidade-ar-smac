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
import org.springframework.test.context.junit4.SpringRunner;

import static org.assertj.core.api.Assertions.assertThat;

@RunWith(SpringRunner.class)
@SpringBootTest
public class BoletimDiarioTest {

    @Autowired
    ResourceLoader resourceLoader;

    @Test
    public void listarMedicoesTest() throws IOException {
        Resource boletimResource = resourceLoader.getResource("classpath:boletim.html");
        String html = new String(Files.readAllBytes(boletimResource.getFile().toPath()));
        BoletimHtmlParser boletimParser = new BoletimHtmlParser(html);
        Resource estacoesResource = resourceLoader.getResource("classpath:estacoes.json");
        String geoJson = new String(Files.readAllBytes(estacoesResource.getFile().toPath()));
        EstacoesGeoJsonParser estacoesParser = new EstacoesGeoJsonParser(geoJson);
        Boletim boletim = boletimParser.obterBoletim(estacoesParser.getFeatureCollection());
        assertThat(boletim.getData()).isEqualTo("02/12/2020");
        assertThat(boletim.getMedicoes().stream().filter(m -> m.getEstacao().getNome().equals("São Cristóvão")).findFirst()).isPresent();
        
        Optional<Medicao> optional = boletim.getMedicoes().stream().filter(m -> m.getEstacao().getNome().equals("Pedra de Guaratiba")).findFirst();
        assertThat(optional).isPresent();
        Medicao medicao = optional.get();
        assertThat(medicao.getEstacao().getLatitude()).isEqualTo(-23.0043789751932);
    }

}
