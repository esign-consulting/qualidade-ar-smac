#!/usr/bin/env python3

import docker
import requests
import time

def healthy():
    try:
        r = requests.head("http://localhost:8080/actuator/health")
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
    container = client.containers.run(image=image, name="smac", remove=True, detach=True, ports={"8080/tcp":"8080"})
else:
    container = containers[0]

i = 1
while not healthy():
    if i > 5:
        print("Max retries exceeded.")
        break
    print("SMAC is not ready. Waiting 2s...")
    time.sleep(2)
    i += 1

print("Stopping %s..." % image)
container.stop()