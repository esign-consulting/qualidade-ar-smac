#!/usr/bin/env python3

from apitimescaledb import TimescaleDB

import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

timescaleDB = TimescaleDB()
boletim = timescaleDB.get_last_boletim()
print(boletim)
