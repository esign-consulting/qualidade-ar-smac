package br.com.esign.qualidadearsmac;

import br.com.esign.qualidadearsmac.model.Boletim;

import java.io.IOException;
import java.nio.file.Files;

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
        Resource resource = resourceLoader.getResource("classpath:boletim.html");
        String html = new String(Files.readAllBytes(resource.getFile().toPath()));
        BoletimHtmlParser parser = new BoletimHtmlParser(html);
        Boletim boletim = parser.obterBoletim();
        assertThat(boletim.getData()).isEqualTo("02/12/2020");
        assertThat(boletim.getMedicoes().stream().filter(m -> m.getEstacao().getNome().equals("São Cristóvão")).findFirst()).isPresent();
    }

}
