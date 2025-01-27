from datetime import datetime

import logging
import requests
import time


class Boletim:

    def __init__(self, data, medicoes):
        self.data = data
        self.medicoes = [Medicao(**m) for m in medicoes]


class Medicao:

    def __init__(self, estacao, classificacao, indice, poluente, medicaoPoluentes):
        self.estacao = Estacao(**estacao)
        self.classificacao = classificacao
        self.indice = indice
        self.poluente = poluente
        self.medicaoPoluentes = [MedicaoPoluente(**mp) for mp in medicaoPoluentes]


class Estacao:

    def __init__(self, nome, codigo, latitude, longitude):
        self.nome = nome
        self.codigo = codigo
        self.latitude = latitude
        self.longitude = longitude


class MedicaoPoluente:

    def __init__(self, poluente, concentracao):
        self.poluente = poluente
        self.concentracao = concentracao


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

    def request(self, data = datetime.today().strftime("%d/%m/%Y")) -> Boletim:
        try:
            self.healthcheck()
            r = requests.get(f"{self.url}/boletim?data={data}")
            return Boletim(**r.json()) if r.status_code == 200 else None
        except Exception as exception:
            logging.error(exception)
            return None 
