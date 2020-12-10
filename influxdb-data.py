#!/usr/bin/env python3

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

if stop:
    print("Stopping %s..." % image)
    container.stop()
