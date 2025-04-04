#!/usr/bin/env python3

from apitimescaledb import TimescaleDB
from datetime import datetime

import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

timescaleDB = TimescaleDB()
boletim = timescaleDB.get_boletim(datetime.strptime("26/12/2024", "%d/%m/%Y").date())
print(boletim)
