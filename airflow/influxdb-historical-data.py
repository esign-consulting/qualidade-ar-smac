#!/usr/bin/env python3

import codecs
import csv
import logging
import requests

from contextlib import closing
from datetime import datetime
from influxdb_client import Point


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

logging.info("Creating the historical-data.line file...")
influxdb_line_file = open("influxdb/historical-data.line", "w")

count = 0
url = "https://hub.arcgis.com/api/v3/datasets/5b1bf5c3e5114564bbf9b7a372b85e17_2/downloads/data?format=csv&spatialRefId=31983"
with closing(requests.get(url, stream=True)) as r:
    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
    for row in reader:
        if row["temp"] != "":
            ts = int(datetime.timestamp(datetime.strptime(row["data"], "%Y/%m/%d %H:%M:%S+00")) * 1e3)
            point = Point("temperatura").tag("estado", "RJ").tag("cidade", "Rio de Janeiro").tag("orgao", "SMAC").tag("estacao", row["estação"]).tag("latitude", row["lat"]).tag("longitude", row["lon"]).field("value", float(row["temp"])).time(ts)
            influxdb_line_file.write("%s\n" % point.to_line_protocol())
            count += 1
            if count % 10000 == 0:
                logging.info(f"{count} lines stored.")

influxdb_line_file.close()
logging.info(f"{count} lines stored. Done.")
