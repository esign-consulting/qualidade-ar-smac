# qualidade-ar-smac

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=esign-consulting_qualidade-ar-smac&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=esign-consulting_qualidade-ar-smac) [![Docker Pulls](https://img.shields.io/docker/pulls/esignbr/qualidade-ar-smac.svg)](https://hub.docker.com/r/esignbr/qualidade-ar-smac) [![API](https://img.shields.io/website-up-down-green-red/http/www.esign.com.br:13887/smac/health.svg?label=API)](http://www.esign.com.br:13887/smac/boletim)

Dados de qualidade do ar coletados da [Prefeitura do RJ - Secretaria Municipal de Meio Ambiente (SMAC)](https://ambienteclima.prefeitura.rio). Os dados são publicados pela SMAC nos seguintes meios:

- [Boletim Diário](http://jeap.rio.rj.gov.br/je-metinfosmac/boletim)
- [Portal de dados abertos da Prefeitura do RJ - Data.Rio](https://www.data.rio/maps/5b1bf5c3e5114564bbf9b7a372b85e17/about)
- [Portal MonitorAr do Ministério de Meio Ambiente e Mudança do Clima](https://monitorar.mma.gov.br)

## Execução

A API é uma aplicação [Spring Boot](https://spring.io/projects/spring-boot) e para ser inicializada execute (requer [Maven](https://maven.apache.org)):

`mvn spring-boot:run`

A API também pode ser inicializada como [contâiner](https://en.wikipedia.org/wiki/Container_Linux). Para inicializar a API deste modo, execute (requer [Docker](https://www.docker.com)):

`docker run --name smac --rm -d -p 8080:8080 esignbr/qualidade-ar-smac`

## Gráfico dos últimos 365 dias

Os dados de qualidade do ar dos últimos 365 dias podem ser carregados para uma base de dados [InfluxDB](https://www.influxdata.com/products/influxdb) e apresentados num dashboard do [Grafana](https://grafana.com). Os passos são os seguintes (requer [Python](https://www.python.org) e [docker-compose](https://docs.docker.com/compose)):

1. Prepare o ambiente Python: `python3 -m venv env && source env/bin/activate && pip3 install -r requirements.txt`;
2. Execute o script Python: `./airflow/influxdb-data.py 365`;
3. Inicialize o ambiente: `docker-compose up -d`;
4. Pelo browser entre em <http://localhost:3000>;
5. Entre no dashboard `SMAC`.

![SMAC dashboard](last365d.png)

### Consultas aos dados

Se preferir, obtenha diretamente todos os dados da SMAC:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear-diaria' --data-urlencode 'q=SELECT * FROM "IQAR" WHERE "orgao" =~ /SMAC/'`

Último índice de qualidade do ar das estações de monitoramento da SMAC:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear-diaria' --data-urlencode 'q=SELECT last(value) AS value FROM "IQAR" WHERE "orgao" =~ /SMAC/ GROUP BY "estacao", "latitude", "longitude"' -s | jq`

Poluentes que mais impactaram o índice de qualidade do ar no período:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear-diaria' --data-urlencode 'q=SELECT count(value) FROM "IQAR" WHERE "orgao" =~ /SMAC/ GROUP BY "poluente"' -s | jq -r '.results[].series[] | "\(.tags.poluente) - \(.values[0][1])"'`

Distribuição da classificação da qualidade do ar no período:

`curl -H 'Authorization: Token my-super-secret-auth-token' -G 'http://localhost:8086/query?db=qualidadear-diaria' --data-urlencode 'q=SELECT count(value) FROM "IQAR" WHERE "orgao" =~ /SMAC/ GROUP BY "classificacao"' -s | jq -r '.results[].series[] | "\(.tags.classificacao) - \(.values[0][1])"'`

## Dados históricos

Dados históricos horários no formato CSV podem ser obtidos do Data.Rio através do comando:

`curl 'https://hub.arcgis.com/api/v3/datasets/5b1bf5c3e5114564bbf9b7a372b85e17_2/downloads/data?format=csv&spatialRefId=31983'`
