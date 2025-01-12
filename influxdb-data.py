#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apidocker import SMAC
from apiinfluxdb import InfluxDB

import datetime
import logging
import sys


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

smac = SMAC()
port = smac.run()
requestor = BoletimRequestor(f"http://localhost:{port}/smac")
influxdb = InfluxDB()

logging.info("Creating the data.line file...")
influxdb_line_file = open("influxdb/data.line", "w")

today = datetime.date.today()
for x in range(int(sys.argv[1]) if len(sys.argv) == 2 else 30):
    days = datetime.timedelta(x)
    past_date = today - days
    d_string = past_date.strftime("%d/%m/%Y")

    boletim = requestor.request(d_string)
    if boletim and boletim.data == d_string:
        for point in influxdb.convert_boletim_to_points_array(boletim):
            influxdb_line_file.write("%s\n" % point.to_line_protocol())
        logging.info(f"Data from {boletim.data} stored.")

influxdb_line_file.close()
logging.info("Done.")

smac.stop()
