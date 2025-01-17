#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apiinfluxdb import InfluxDB
from apidocker import SMAC

import datetime
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

smac = SMAC()
port = smac.run()
requestor = BoletimRequestor(f"http://localhost:{port}/smac")
influxdb = InfluxDB()

logging.info("Writing to influxDB...")
last_date = influxdb.get_last_timestamp().date()
next_date = last_date + datetime.timedelta(1)
today = datetime.date.today()
while next_date <= today:
    d_string = next_date.strftime("%d/%m/%Y")
    boletim = requestor.request(d_string)
    if boletim and boletim.data == d_string:
        influxdb.write_boletim(boletim)
        logging.info(f"Data from {boletim.data} written.")
    next_date = next_date + datetime.timedelta(1)

logging.info("Done.")
smac.stop()
