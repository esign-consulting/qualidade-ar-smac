from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago

with DAG(dag_id="test", start_date=days_ago(1), schedule="0 0 * * *") as dag:

    @task()
    def airflow():
        print("airflow")
