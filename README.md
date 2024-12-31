# qualidade-ar-smac

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=esign-consulting_qualidade-ar-smac&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=esign-consulting_qualidade-ar-smac) [![Docker Pulls](https://img.shields.io/docker/pulls/esignbr/qualidade-ar-smac.svg)](https://hub.docker.com/r/esignbr/qualidade-ar-smac) [![API](https://img.shields.io/website-up-down-green-red/http/www.esign.com.br:13887/actuator/health.svg?label=API)](http://www.esign.com.br:13887/boletim)

Dados de qualidade do ar coletados da [Prefeitura do RJ - Secretaria Municipal de Meio Ambiente (SMAC)](https://ambienteclima.prefeitura.rio). Os dados publicados em <http://jeap.rio.rj.gov.br/je-metinfosmac/boletim> em formato [HTML](https://en.wikipedia.org/wiki/HTML) são interpretados e disponibilizados por uma [API](https://en.wikipedia.org/wiki/API) em formato [JSON](https://en.wikipedia.org/wiki/JSON). Isso permite que sejam mais facilmente consumidos por outros sistemas de informação.

## Execução

A API é uma aplicação [Spring Boot](https://spring.io/projects/spring-boot) e para ser inicializada execute (requer [Maven](https://maven.apache.org)):

`mvn spring-boot:run`

A API também pode ser inicializada como [contâiner](https://en.wikipedia.org/wiki/Container_Linux). Isso traz praticidade para implantá-la em sistemas operacionais diversos. Para inicializar a API deste modo, execute (requer [Docker](https://www.docker.com)):

`docker run --name smac -d -p 8080:8080 esignbr/qualidade-ar-smac`

Após inicializar, abra o browser e entre em <http://localhost:8080/boletim>. Os dados mais recentes de qualidade do ar publicados pela SMAC serão apresentados em formato JSON.

Se quiser obter os dados publicados numa data específica, informe o campo `data`. Por exemplo, para obter os dados de `24/03/2021`, entre em <http://localhost:8080/boletim?data=24/03/2021>.

## Gráfico dos últimos 365 dias

Os dados de qualidade do ar dos últimos 365 dias podem ser carregados para uma base de dados [InfluxDB](https://www.influxdata.com/products/influxdb) e apresentados num dashboard do [Grafana](https://grafana.com). Os passos são os seguintes (requer [Python](https://www.python.org) e [docker-compose](https://docs.docker.com/compose)):

1. Prepare o ambiente Python: `python3 -m venv env && source env/bin/activate && pip3 install -r requirements.txt`;
2. Execute o script Python: `./influxdb-data.py 365`;
3. Inicialize o ambiente: `docker-compose up -d`;
4. Pelo browser entre em <http://localhost:3000>;
5. Entre no dashboard `SMAC`.

![SMAC dashboard](last365d.png)

### Consultas aos dados

Se preferir, obtenha diretamente todos os dados da SMAC:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear' --data-urlencode 'q=SELECT * FROM "IQAR" WHERE "orgao" =~ /SMAC/'`

Último índice de qualidade do ar das estações de monitoramento da SMAC:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear' --data-urlencode 'q=SELECT last(value) AS value FROM "IQAR" WHERE "orgao" =~ /SMAC/ GROUP BY "estacao", "latitude", "longitude"' -s | jq`

Poluentes que mais impactaram o índice de qualidade do ar no período:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear' --data-urlencode 'q=SELECT count(value) FROM "IQAR" WHERE "orgao" =~ /SMAC/ GROUP BY "poluente"' -s | jq -r '.results[].series[] | "\(.tags.poluente) - \(.values[0][1])"'`

Distribuição da classificação da qualidade do ar no período:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear' --data-urlencode 'q=SELECT count(value) FROM "IQAR" WHERE "orgao" =~ /SMAC/ GROUP BY "classificacao"' -s | jq -r '.results[].series[] | "\(.tags.classificacao) - \(.values[0][1])"'`

## Portal MonitorAr do Ministério de Meio Ambiente e Mudança do Clima

Estações de monitoramento da qualidade do ar:

`curl https://monitorar-backend.mma.gov.br/v1/estacao/todas -s | jq -r '.[] | "\(.noFonteDados) - \(.noEstacao)"' | sort`

Estações de monitoramento da SMAC:

`curl https://monitorar-backend.mma.gov.br/v1/estacao/todas -s | jq -r '.[] | select(.noFonteDados | contains("SMAC")) | "\(.idEstacao) - \(.noEstacao)"' | sort`

Dados horários das estações de monitoramento da SMAC:

`curl https://monitorar-backend.mma.gov.br/v1/estacao/por-ids?ids=381,382,383,384,385,386,387,401 -s | jq`
