#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apitimescaledb import TimescaleDB

import datetime
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

requestor = BoletimRequestor("http://www.esign.com.br:13887/smac")
today = datetime.date.today()
d_string = today.strftime("%d/%m/%Y")
boletim = requestor.request(d_string)

if boletim:
    logging.info(f"Boletim of {boletim.data} obtained.")
    timescaleDB = TimescaleDB()
    timescaleDB.insert_boletim(boletim)
