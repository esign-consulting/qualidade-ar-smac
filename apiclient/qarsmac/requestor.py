import datetime
import logging
import requests
import time
from qarsmac.model import Boletim


class HealthcheckMaxRetriesExceededError(Exception):

    def __init__(self, *args):
        super().__init__("Max retries exceeded.")


class BoletimRequestor:

    def __init__(self, url = "http://localhost:8080/smac", healthcheck_max_retries = 5, healthcheck_retry_delay = 2):
        self.url = url
        self.healthcheck_max_retries = healthcheck_max_retries
        self.healthcheck_retry_delay = healthcheck_retry_delay

    def healthy(self) -> bool:
        try:
            r = requests.head(f"{self.url}/health")
            return r.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        
    def healthcheck(self) -> None:
        i = 1
        while not self.healthy():
            if i > self.healthcheck_max_retries:
                raise HealthcheckMaxRetriesExceededError()
            logging.info(f"SMAC is not ready. Waiting {self.healthcheck_retry_delay}s (attempt {i} of {self.healthcheck_max_retries})...")
            time.sleep(self.healthcheck_retry_delay)
            i += 1

    def request(self, data: datetime.date = datetime.date.today()) -> Boletim:
        try:
            self.healthcheck()
            d_string = data.strftime("%d/%m/%Y")
            logging.info(f"Requesting data for {d_string}...")
            r = requests.get(f"{self.url}/boletim?data={d_string}")
            return Boletim(**r.json()) if r.status_code == 200 else None
        except Exception as exception:
            logging.error(exception)
            return None 
