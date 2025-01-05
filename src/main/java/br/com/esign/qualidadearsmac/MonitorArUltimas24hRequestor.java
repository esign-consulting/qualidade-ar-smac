package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import com.fasterxml.jackson.databind.JsonNode;

public class MonitorArUltimas24hRequestor  extends Requestor {

    public static final String URL_DADOS_HORARIOS = "https://monitorar-backend.mma.gov.br/v1/estacao/por-ids";

    private String url;
    private JsonNode monitorArEstacoesJsonNode;

    public MonitorArUltimas24hRequestor() {
        this(URL_DADOS_HORARIOS, null);
    }

    public MonitorArUltimas24hRequestor(JsonNode monitorArEstacoesJsonNode) {
        this(URL_DADOS_HORARIOS, monitorArEstacoesJsonNode);
    }

    public MonitorArUltimas24hRequestor(String url, JsonNode monitorArEstacoesJsonNode) {
        this.url = url;
        this.monitorArEstacoesJsonNode = monitorArEstacoesJsonNode;
    }

    public String request() throws IOException {
        String ids = null;
        if (monitorArEstacoesJsonNode != null) {
            List<String> idsList = new ArrayList<>(monitorArEstacoesJsonNode.size());
            Iterator<JsonNode> nodes = monitorArEstacoesJsonNode.elements();
            while (nodes.hasNext()) {
                idsList.add(nodes.next().get("idEstacao").asText());
            }
            ids = String.join(",", idsList);
        }
        return request((ids == null) ? url : url.concat(String.format("?ids=%s", ids)));
    }

}
