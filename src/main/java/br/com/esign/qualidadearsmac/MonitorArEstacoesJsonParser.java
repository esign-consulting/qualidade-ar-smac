package br.com.esign.qualidadearsmac;

import java.io.IOException;
import java.util.Iterator;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class MonitorArEstacoesJsonParser {

    private final JsonNode monitorArEstacoesJsonNode;

    public MonitorArEstacoesJsonParser() throws IOException {
        this(new MonitorArEstacoesJsonRequestor());
    }

    public MonitorArEstacoesJsonParser(MonitorArEstacoesJsonRequestor requestor) throws IOException {
        this(requestor.request());
    }

    public MonitorArEstacoesJsonParser(String monitorArEstacoesJson) throws JsonProcessingException {
        monitorArEstacoesJsonNode = new ObjectMapper().readTree(monitorArEstacoesJson);
        Iterator<JsonNode> nodes = monitorArEstacoesJsonNode.elements();
        while (nodes.hasNext()) {
            if (!nodes.next().get("noFonteDados").textValue().contains("SMAC")) {
                nodes.remove();
            }
        }
    }

    public JsonNode getMonitorArEstacoesJsonNode() {
        return monitorArEstacoesJsonNode;
    }

}
