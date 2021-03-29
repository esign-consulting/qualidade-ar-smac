# qualidade-ar-smac

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Docker Build status](https://img.shields.io/docker/cloud/build/esignbr/qualidade-ar-smac.svg)](https://hub.docker.com/r/esignbr/qualidade-ar-smac/builds) [![Docker Pulls](https://img.shields.io/docker/pulls/esignbr/qualidade-ar-smac.svg)](https://hub.docker.com/r/esignbr/qualidade-ar-smac)

Dados de qualidade do ar coletados da [Prefeitura do RJ - Secretaria Municipal de Meio Ambiente (SMAC)](https://www.rio.rj.gov.br/web/smac). Os dados publicados em <http://jeap.rio.rj.gov.br/je-metinfosmac/boletim> em formato [HTML](https://en.wikipedia.org/wiki/HTML) são interpretados e disponibilizados por uma [API](https://en.wikipedia.org/wiki/API) em formato [JSON](https://en.wikipedia.org/wiki/JSON). Isso permite que sejam mais facilmente consumidos por outros sistemas de informação.

## Execução

A API é uma aplicação [Spring Boot](https://spring.io/projects/spring-boot) e para ser inicializada execute (requer [Maven](https://maven.apache.org)):

`mvn spring-boot:run`

A API também pode ser inicializada como [contâiner](https://en.wikipedia.org/wiki/Container_Linux). Isso traz praticidade para implantá-la em sistemas operacionais diversos. Para inicializar a API deste modo, execute (requer [Docker](https://www.docker.com)):

`docker run --name smac -d -p 8080:8080 esignbr/qualidade-ar-smac`

Após inicializar, abra o browser e entre em <http://localhost:8080/boletim>. Os dados mais recentes de qualidade do ar publicados pela SMAC serão apresentados em formato JSON.

Se quiser obter os dados publicados numa data específica, informe o campo `data`. Por exemplo, para obter os dados de `24/03/2021`, entre em <http://localhost:8080/boletim?data=24/03/2021>.

## InfluxDB

Os dados de qualidade do ar dos últimos 30 dias podem ser carregados para uma base de dados [InfluxDB](https://www.influxdata.com/products/influxdb). Os passos são os seguintes:

1. Prepare o ambiente Python: `python3 -m venv env && source env/bin/activate && pip3 install -r requirements.txt`
2. Execute o script Python: `./influxdb-data.py`
3. Inicialize a base de dados: `docker-compose up -d`
4. Pesquise os dados: `curl -H 'Authorization: Token grafana:ReaderSecret' -G 'http://localhost:8086/query?db=iqar' --data-urlencode 'q=SELECT * FROM "iqar"'`
