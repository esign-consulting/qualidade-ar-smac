package br.com.esign.qualidadearsmac;

import java.io.IOException;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

public class BoletimHtmlRequestor {

    public static final String URL_BOLETIM = "http://jeap.rio.rj.gov.br/je-metinfosmac/boletim";

    private String url;
    private String data;

    public BoletimHtmlRequestor() {
        this(URL_BOLETIM, null);
    }

    public BoletimHtmlRequestor(String data) {
        this(URL_BOLETIM, data);
    }

    public BoletimHtmlRequestor(String url, String data) {
        this.url = url;
        this.data = data;
    }

    public String request() throws IOException {
        CloseableHttpClient httpclient = HttpClients.createDefault();
        try {
            HttpGet httpget = new HttpGet((data == null) ? url : url.concat(String.format("?data=%s", data)));
            ResponseHandler<String> responseHandler = new ResponseHandler<String>() {

                @Override
                public String handleResponse(HttpResponse response) throws ClientProtocolException, IOException {
                    int status = response.getStatusLine().getStatusCode();
                    if (status >= 200 && status < 300) {
                        HttpEntity entity = response.getEntity();
                        return entity != null ? EntityUtils.toString(entity) : null;
                    } else {
                        throw new ClientProtocolException("Unexpected response status: " + status);
                    }
                }

            };
            String responseBody = httpclient.execute(httpget, responseHandler);
            return responseBody;
        } finally {
            httpclient.close();
        }
    }

}
