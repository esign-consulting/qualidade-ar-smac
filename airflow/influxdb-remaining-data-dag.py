from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago

from apiclient import BoletimRequestor
from apiinfluxdb import InfluxDB

import datetime
import logging

with DAG(dag_id="smac_etl", start_date=days_ago(1), schedule="0 0 * * *") as dag:

    @task
    def influxdb_remaining_data():
        requestor = BoletimRequestor(url="http://smac:8080/smac")
        influxdb = InfluxDB(url="http://influxdb:8086")

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

    influxdb_remaining_data()
