package br.com.esign.qualidadearsmac;

import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.nio.file.Files;

import org.geojson.FeatureCollection;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.test.context.junit4.SpringRunner;

@RunWith(SpringRunner.class)
@SpringBootTest
public class EstacoesGeoJsonTest {

    @Autowired
    ResourceLoader resourceLoader;

    @Test
    public void listarMedicoesTest() throws IOException {
        Resource resource = resourceLoader.getResource("classpath:estacoes.json");
        String geoJson = new String(Files.readAllBytes(resource.getFile().toPath()));
        EstacoesGeoJsonParser parser = new EstacoesGeoJsonParser(geoJson);
        FeatureCollection featureCollection = parser.getFeatureCollection();
        assertTrue(featureCollection.getFeatures().stream().filter(f -> f.getProperty("nome").equals("ESTAÇÃO BANGU")).findFirst().isPresent());
    }

}
