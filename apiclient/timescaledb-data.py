#!/usr/bin/env python3

from apiclient import BoletimRequestor
from qarsmac.timescaledb import TimescaleDB

import datetime
import logging
import sys


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

requestor = BoletimRequestor("https://qualidadearsmac.azurewebsites.net/api")
timescaleDB = TimescaleDB()

logging.info("Storing into TimescaleDB...")
today = datetime.date.today()
for x in reversed(range(int(sys.argv[1]) if len(sys.argv) == 2 else 30)):
    days = datetime.timedelta(x)
    past_date = today - days
    boletim = requestor.request(past_date)
    if boletim and boletim.data == past_date:
        timescaleDB.insert_boletim(boletim)
        logging.info(f"Data from {boletim.data} stored.")

logging.info("Done.")
