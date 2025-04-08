#!/usr/bin/env python3

from apitimescaledb import TimescaleDB

import datetime
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

timescaleDB = TimescaleDB()

boletim_date = timescaleDB.get_first_boletim_data()
logging.info(f"First date: {boletim_date}")
last_boletim_date = timescaleDB.get_last_boletim_data()
logging.info(f"Last date: {last_boletim_date}")

# Get all boletins
is_valid_count = 0
is_invalid_count = 0
while boletim_date <= last_boletim_date:
    boletim = timescaleDB.get_boletim(boletim_date)
    if boletim:
        logging.info(f"Checking boletim {boletim.data}...")
        if boletim.is_valid():
            is_valid_count += 1
            logging.info(f"Boletim {boletim.data} is valid.")
        else:
            is_invalid_count += 1
            logging.info(f"Boletim {boletim.data} is invalid.")
    boletim_date += datetime.timedelta(1)

# Print the total number of boletins
logging.info(f"Total boletins: {is_valid_count + is_invalid_count}")

# Print the number of valid and invalid boletins
logging.info(f"Valid boletins: {is_valid_count}")
logging.info(f"Invalid boletins: {is_invalid_count}")
