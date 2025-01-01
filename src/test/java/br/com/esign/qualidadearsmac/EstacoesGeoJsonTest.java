package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.nio.file.Files;

import org.geojson.FeatureCollection;
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
public class EstacoesGeoJsonTest {

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void listarEstacoesTest() throws IOException {
        Resource resource = resourceLoader.getResource("classpath:estacoes.json");
        String geoJson = new String(Files.readAllBytes(resource.getFile().toPath()));
        EstacoesGeoJsonParser parser = new EstacoesGeoJsonParser(geoJson);
        FeatureCollection featureCollection = parser.getFeatureCollection();
        assertThat(featureCollection.getFeatures().stream().filter(f -> f.getProperty("nome").equals("ESTAÇÃO BANGU")).findFirst()).isPresent();
    }

}
