package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.nio.file.Files;
import java.util.HashMap;

import org.assertj.core.util.Streams;
import org.json.JSONException;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.skyscreamer.jsonassert.JSONAssert;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import static org.assertj.core.api.Assertions.assertThat;

@ContextConfiguration(classes = Application.class)
@RunWith(SpringRunner.class)
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
public class ControllerTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void obterBoletimTest() throws IOException, JSONException {
        Resource boletimResource = resourceLoader.getResource("classpath:boletim.json");
        String expected = new String(Files.readAllBytes(boletimResource.getFile().toPath()));
        String url = String.format("http://localhost:%s/smac/boletim?data=26/12/2024", port);
        String actual = restTemplate.getForObject(url, String.class);
        JSONAssert.assertEquals(expected, actual, false);
	}

    @Test
    public void invalidDataBoletimTest() throws IOException {
        String url = String.format("http://localhost:%s/smac/boletim?data=01/13/2016", port);
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        HashMap<String, String> responseJsonFields = new ObjectMapper().readValue(response.getBody(), new TypeReference<HashMap<String, String>>() {});
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(responseJsonFields).containsEntry("message", "Data inválida. O formato da data deve ser DD/MM/AAAA.");
	}

    @Test
    public void boletimNaoEncontradoTest() throws IOException {
        String url = String.format("http://localhost:%s/smac/boletim?data=01/08/2016", port);
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        HashMap<String, String> responseJsonFields = new ObjectMapper().readValue(response.getBody(), new TypeReference<HashMap<String, String>>() {});
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(responseJsonFields).containsEntry("message", "Boletim não encontrado. A data do boletim deve ser posterior a 01/08/2016.");
	}

    @Test
    public void listarMonitorArUltimas24hTest() throws IOException {
        String url = String.format("http://localhost:%s/smac/monitorar/ultimas24h", port);
        String ultimas24hJson = restTemplate.getForObject(url, String.class);
        JsonNode ultimas24hJsonNode = new ObjectMapper().readTree(ultimas24hJson);
        assertThat(Streams.stream(ultimas24hJsonNode.elements()).filter(n-> !n.get("noFonteDados").textValue().contains("SMAC")).findFirst()).isNotPresent();
	}

}
