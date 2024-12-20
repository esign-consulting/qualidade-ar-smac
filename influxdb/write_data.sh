#!/bin/bash
set -e

influx write -b ${DOCKER_INFLUXDB_INIT_BUCKET_ID} -f /docker-entrypoint-initdb.d/data.line
