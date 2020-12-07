package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.nio.file.Files;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.test.context.junit4.SpringRunner;

import static org.assertj.core.api.Assertions.*;

@RunWith(SpringRunner.class)
@SpringBootTest
public class BoletimDiarioTest {

    @Autowired
    ResourceLoader resourceLoader;

    @Test
    public void listarMedicoesTest() throws IOException {
        Resource resource = resourceLoader.getResource("classpath:boletim.html");
        String html = new String(Files.readAllBytes(resource.getFile().toPath()));
        BoletimDiario boletimDiario = new BoletimDiario(html);
        List<Medicao> medicoes = boletimDiario.listarMedicoes();
        Medicao medicao = medicoes.get(0);
        assertThat(medicao.getData()).isEqualTo("02/12/2020");
    }

}
