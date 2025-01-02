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
    public void getJsonNodeTest() throws IOException {
        Resource resource = resourceLoader.getResource("classpath:estacoes-monitorar.json");
        String json = new String(Files.readAllBytes(resource.getFile().toPath()));
        MonitorArEstacoesJsonParser parser = new MonitorArEstacoesJsonParser(json);
        JsonNode jsonNode = parser.getJsonNode();
        assertThat(Streams.stream(jsonNode.elements()).filter(n-> !n.get("noFonteDados").textValue().contains("SMAC")).findFirst()).isNotPresent();
    }

}
