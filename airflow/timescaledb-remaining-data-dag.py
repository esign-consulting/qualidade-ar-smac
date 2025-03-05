from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago

from apiclient import BoletimRequestor
from apitimescaledb import TimescaleDB

import datetime
import logging

with DAG(dag_id="smac_etl", start_date=days_ago(1), schedule="0 0 * * *") as dag:

    @task
    def timescaledb_remaining_data():
        requestor = BoletimRequestor("http://www.esign.com.br:13887/smac")
        timescaleDB = TimescaleDB(host="timescaledb")

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

    timescaledb_remaining_data()
