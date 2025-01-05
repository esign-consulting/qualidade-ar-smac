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
public class EstacoesGeoJsonParserTest {

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void getDataRioEstacoesFeatureCollectionTest() throws IOException {
        Resource dataRioEstacoesResource = resourceLoader.getResource("classpath:datario-estacoes.json");
        String dataRioEstacoesGeoJson = new String(Files.readAllBytes(dataRioEstacoesResource.getFile().toPath()));
        DataRioEstacoesGeoJsonParser estacoesParser = new DataRioEstacoesGeoJsonParser(dataRioEstacoesGeoJson);
        FeatureCollection dataRioEstacoesFeatureCollection = estacoesParser.getDataRioEstacoesFeatureCollection();
        assertThat(dataRioEstacoesFeatureCollection.getFeatures().stream().filter(f -> f.getProperty("nome").equals("ESTAÇÃO BANGU")).findFirst()).isPresent();
    }

}
