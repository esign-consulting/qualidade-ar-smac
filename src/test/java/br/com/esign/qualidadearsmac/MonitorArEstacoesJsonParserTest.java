package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.nio.file.Files;

import org.assertj.core.util.Streams;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import com.fasterxml.jackson.databind.JsonNode;

import static org.assertj.core.api.Assertions.assertThat;

@ContextConfiguration(classes = Application.class)
@RunWith(SpringRunner.class)
@SpringBootTest
public class MonitorArEstacoesJsonParserTest {

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void getMonitorArEstacoesJsonNodeTest() throws IOException {
        Resource monitorArEstacoesResource = resourceLoader.getResource("classpath:estacoes-monitorar.json");
        String monitorArEstacoesJson = new String(Files.readAllBytes(monitorArEstacoesResource.getFile().toPath()));
        MonitorArEstacoesJsonParser estacoesParser = new MonitorArEstacoesJsonParser(monitorArEstacoesJson);
        JsonNode monitorArEstacoesJsonNode = estacoesParser.getMonitorArEstacoesJsonNode();
        assertThat(Streams.stream(monitorArEstacoesJsonNode.elements()).filter(n-> !n.get("noFonteDados").textValue().contains("SMAC")).findFirst()).isNotPresent();
    }

}
