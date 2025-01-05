#!/usr/bin/env python3

import datetime
import docker
import logging
import requests
import socket
import sys
import time

def get_port(port=8080):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port <= port + 10:
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError('no free ports')

def healthy(port):
    try:
        endpoint = f"http://localhost:{port}/smac/health"
        r = requests.head(endpoint)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def escape_tag_value(value):
    return value.replace(' ', '\ ').replace(',', '\,')

def get_medicao_poluente(medicao, poluente):
    for medicao_poluente in medicao["medicaoPoluentes"]:
        if medicao_poluente["poluente"] == poluente or medicao_poluente["poluente"].find(poluente) > -1:
            return medicao_poluente
    return None

def get_concentracao(medicao_poluente):
    if medicao_poluente:
        try:
            concentracao = float(medicao_poluente["concentracao"].replace(',', '.'))
            return concentracao
        except ValueError:
            return None
    else:
        return None

def write_line_concentracao_poluente(line_file, poluente):
    concentracao = get_concentracao(get_medicao_poluente(medicao, poluente))
    if concentracao:
        line_file.write(f"{poluente.replace(',', '.')},estado=RJ,cidade=Rio\ de\ Janeiro,orgao=SMAC,estacao={estacao},latitude={latitude},longitude={longitude} value={concentracao} {ts}\n")

logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

client = docker.from_env()
image = "esignbr/qualidade-ar-smac"

if not client.images.list(name=image):
    logging.info(f"Building {image}...")
    client.images.build(tag=image, path=".")

containers = client.containers.list(filters={"ancestor":image})
if not containers:
    logging.info(f"Running {image}...")
    port = get_port()
    container = client.containers.run(image=image, name="smac", remove=True, detach=True, ports={"8080/tcp":port})
    stop = True
else:
    container = containers[0]
    port = int(container.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"])
    stop = False

i = 1
while not healthy(port):
    if i > 5:
        logging.info("Max retries exceeded.")
        break
    logging.info("SMAC is not ready. Waiting 2s...")
    time.sleep(2)
    i += 1

logging.info("Creating the data.line file...")
iqar_line_file = open("influxdb/data.line", "w")

today = datetime.date.today()
for x in range(int(sys.argv[1]) if len(sys.argv) == 2 else 30):
    days = datetime.timedelta(x)
    date = today - days
    ts = int(datetime.datetime.timestamp(datetime.datetime.combine(date, datetime.datetime.min.time())) * 1000000000)
    d_string = date.strftime("%d/%m/%Y")

    url = "http://localhost:%s/smac/boletim?data=%s" % (port, d_string)
    r = requests.get(url)
    if r.status_code == 200:
        boletim = r.json()
        if boletim["data"] == d_string:
            for medicao in boletim["medicoes"]:
                estacao = escape_tag_value(medicao["estacao"]["nome"])
                latitude = medicao["estacao"]["latitude"]
                longitude = medicao["estacao"]["longitude"]
                poluente = escape_tag_value(medicao["poluente"])
                classificacao = escape_tag_value(medicao["classificacao"])
                iqar_line_file.write(f"IQAR,estado=RJ,cidade=Rio\ de\ Janeiro,orgao=SMAC,estacao={estacao},latitude={latitude},longitude={longitude},poluente={poluente},classificacao={classificacao} value={medicao['indice']} {ts}\n")
                write_line_concentracao_poluente(iqar_line_file, "MP10")
                write_line_concentracao_poluente(iqar_line_file, "MP2,5")
                write_line_concentracao_poluente(iqar_line_file, "O3")
                write_line_concentracao_poluente(iqar_line_file, "CO")
                write_line_concentracao_poluente(iqar_line_file, "NO2")
                write_line_concentracao_poluente(iqar_line_file, "SO2")
            logging.info(f"Data from {boletim['data']} stored.")

iqar_line_file.close()
logging.info("Done.")

if stop:
    container.stop()
    logging.info(f"{image} stopped.")
