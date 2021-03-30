#!/usr/bin/env python3

import datetime
import docker
import requests
import socket
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
        endpoint = "http://localhost:%s/actuator/health" % port
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

def iql_insert_concentracao_poluente(iql_file, poluente):
    concentracao = get_concentracao(get_medicao_poluente(medicao, poluente))
    if concentracao:
        iql_file.write('INSERT %s,estado=RJ,cidade=Rio\ de\ Janeiro,orgao=SMAC,estacao=%s value=%s %s\n' % (poluente, estacao, concentracao, ts))

client = docker.from_env()
image = "esignbr/qualidade-ar-smac"

if not client.images.list(name=image):
    print("Building %s..." % image)
    client.images.build(tag=image, path=".")

containers = client.containers.list(filters={"ancestor":image})
if not containers:
    print("Running %s..." % image)
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
        print("Max retries exceeded.")
        break
    print("SMAC is not ready. Waiting 2s...")
    time.sleep(2)
    i += 1

print("Creating the last30d.iql file...")
iqar_iql_file = open("influxdb/last30d.iql", "w")
iqar_iql_file.write('USE qualidadear;\n')

today = datetime.date.today()
for x in range(30):
    days = datetime.timedelta(x)
    date = today - days
    ts = int(datetime.datetime.timestamp(datetime.datetime.combine(date, datetime.datetime.min.time())) * 1000000000)
    d_string = date.strftime("%d/%m/%Y")

    url = "http://localhost:%s/boletim?data=%s" % (port, d_string)
    r = requests.get(url)
    if r.status_code == 200:
        boletim = r.json()
        for medicao in boletim["medicoes"]:
            estacao = escape_tag_value(medicao["estacao"])
            poluente = escape_tag_value(medicao["poluente"])
            classificacao = escape_tag_value(medicao["classificacao"])
            iqar_iql_file.write('INSERT IQAR,estado=RJ,cidade=Rio\ de\ Janeiro,orgao=SMAC,estacao=%s,poluente=%s,classificacao=%s value=%s %s\n' % (estacao, poluente, classificacao, medicao["indice"], ts))
            iql_insert_concentracao_poluente(iqar_iql_file, "MP10")
            iql_insert_concentracao_poluente(iqar_iql_file, "O3")
            iql_insert_concentracao_poluente(iqar_iql_file, "CO")
            iql_insert_concentracao_poluente(iqar_iql_file, "SO2")

iqar_iql_file.close()

if stop:
    print("Stopping %s..." % image)
    container.stop()
