from datetime import datetime
import requests


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

    def __init__(self, nome, latitude, longitude):
        self.nome = nome
        self.latitude = latitude
        self.longitude = longitude


class MedicaoPoluente:

    def __init__(self, poluente, concentracao):
        self.poluente = poluente
        self.concentracao = concentracao


class Requestor:

    def __init__(self, url = "http://localhost:8080/smac"):
        self.url = url

    def request(self, data = datetime.today().strftime("%d/%m/%Y")) -> Boletim:
        try:
            r = requests.get(f"{self.url}/boletim?data={data}")
            return Boletim(**r.json()) if r.status_code == 200 else None
        except Exception:
            return None 
