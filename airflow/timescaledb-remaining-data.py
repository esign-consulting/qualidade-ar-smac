#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apitimescaledb import TimescaleDB

import datetime
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

requestor = BoletimRequestor("http://www.esign.com.br:13887/smac")
timescaleDB = TimescaleDB()

logging.info("Storing into TimescaleDB...")
last_date = timescaleDB.get_last_boletim_data()
next_date = last_date + datetime.timedelta(1)
today = datetime.date.today()
while next_date <= today:
    d_string = next_date.strftime("%d/%m/%Y")
    boletim = requestor.request(d_string)
    if boletim and boletim.data == d_string:
        timescaleDB.insert_boletim(boletim)
        logging.info(f"Data from {boletim.data} stored.")
    next_date = next_date + datetime.timedelta(1)

logging.info("Done.")
