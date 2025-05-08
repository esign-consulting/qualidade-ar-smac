#!/usr/bin/env python3

from apiclient import BoletimRequestor
from qarsmac.timescaledb import TimescaleDB

import datetime
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

requestor = BoletimRequestor("https://qualidadearsmac.azurewebsites.net/api")
timescaleDB = TimescaleDB()

logging.info("Storing into TimescaleDB...")
last_date = timescaleDB.get_last_boletim_data()
next_date = last_date + datetime.timedelta(1)
today = datetime.date.today()
while next_date <= today:
    boletim = requestor.request(next_date)
    if boletim and boletim.data == next_date:
        timescaleDB.insert_boletim(boletim)
        logging.info(f"Data from {boletim.data} stored.")
    next_date += datetime.timedelta(1)

logging.info("Done.")
