#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apidocker import SMAC
from apiinfluxdb import InfluxDB

import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

smac = SMAC()
port = smac.run()
requestor = BoletimRequestor(f"http://localhost:{port}/smac")
boletim = requestor.request()
smac.stop()

if boletim:
    influxdb = InfluxDB()
    for point in influxdb.convert_boletim_to_points_array(boletim):
        print(point.to_line_protocol())
