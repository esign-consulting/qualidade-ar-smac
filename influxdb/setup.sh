#!/bin/bash
set -e

influx write -b ${DOCKER_INFLUXDB_INIT_BUCKET_ID} -f /docker-entrypoint-initdb.d/data.line

influx bucket create -n qualidadear-horaria
influx write -b qualidadear-horaria -f /docker-entrypoint-initdb.d/historical-data.line
