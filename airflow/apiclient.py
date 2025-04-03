from datetime import datetime

import json
import logging
import requests
import time


class MedicaoPoluente:

    def __init__(self, poluente, concentracao):
        self.poluente = Poluente(poluente)
        try:
            self.concentracao = float(concentracao.replace(',', '.'))
        except ValueError:
            self.concentracao = None

    def __str__(self):
        return json.dumps(vars(self), default=str, ensure_ascii=False)


class Estacao:

    def __init__(self, nome, codigo, latitude, longitude):
        self.nome = nome
        self.codigo = codigo
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return json.dumps(vars(self), ensure_ascii=False)

    def __eq__(self, other):
        return isinstance(other, Estacao) and vars(self) == vars(other)

    def __hash__(self):
        return hash({"estacao": vars(self)})


class Poluente:

    def __init__(self, poluente):
        self.poluente = poluente
        self.nome = poluente[0 : poluente.find("(") - 1]
        self.codigo = poluente[poluente.find("(") + 1 : poluente.find(")")]
        if "[" in poluente and "]" in poluente:
            self.unidade_concentracao = poluente[poluente.find("[") + 1 : poluente.find("]")]

    def __str__(self):
        return self.poluente

    def __eq__(self, other):
        return isinstance(other, Poluente) and self.codigo == other.codigo

    def __hash__(self):
        return hash(f"Poluente {self.codigo}")


class Medicao:

    def __init__(self, estacao, classificacao, indice, poluente, medicaoPoluentes):
        self.estacao = Estacao(**estacao)
        self.classificacao = classificacao
        try:
            self.indice = float(indice.replace(',', '.'))
        except ValueError:
            self.indice = None
        self.poluente = Poluente(poluente)
        self.medicaoPoluentes = [MedicaoPoluente(**mp) for mp in medicaoPoluentes]

    @property
    def poluentes(self) -> list[Poluente]:
        return [mp.poluente for mp in self.medicaoPoluentes
                if self.get_concentracao_poluente(mp.poluente.codigo)]

    def get_concentracao_poluente(self, codigo_poluente: str) -> float:
        medicao_poluente = next((mp for mp in self.medicaoPoluentes
                                 if codigo_poluente == mp.poluente.codigo), None)
        return medicao_poluente.concentracao if medicao_poluente else None

    def is_valid(self) -> bool:
        iqar_calculator = IQArCalculator()
        return iqar_calculator.calc_from_medicao(self) == (self.poluente.codigo, self.classificacao, self.indice)

    def __str__(self):
        return json.dumps(vars(self), default=str, ensure_ascii=False)


class Boletim:

    def __init__(self, data, medicoes):
        self.data = data
        self.medicoes = [Medicao(**m) for m in medicoes]

    @property
    def estacoes(self) -> list[Estacao]:
        return [m.estacao for m in self.medicoes]
    
    @property
    def poluentes(self) -> list[Poluente]:
        poluentes = []
        for m in self.medicoes:
            poluentes = list(set(poluentes + m.poluentes))
        return poluentes

    def is_valid(self) -> bool:
        for m in self.medicoes:
            if not m.is_valid():
                return False
        return True

    def __str__(self):
        return json.dumps(vars(self), default=str, ensure_ascii=False)


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



class IQArCalculator:

    def __init__(self):
        self.iqarTable = {
            "qualidadeAr": ["Boa", "Moderada", "Ruim", "Muito Ruim", "Péssima"],
            "indice": [range(0, 41), range(41, 81), range(81, 121), range(121, 201), range(201, 401)],
            "MP10": [range(0, 51), range(51, 101), range(101, 151), range(151, 251), range(251, 601)],
            "MP2,5": [range(0, 26), range(26, 51), range(51, 76), range(76, 126), range(126, 301)],
            "O3": [range(0, 101), range(101, 131), range(131, 161), range(161, 201), range(201, 801)],
            "CO": [range(0, 10), range(10, 12), range(12, 14), range(14, 16), range(16, 51)],
            "NO2": [range(0, 201), range(201, 241), range(241, 321), range(321, 1131), range(1131, 3751)],
            "SO2": [range(0, 21), range(21, 41), range(41, 366), range(366, 801), range(801, 2621)]
        }

    def calc(self, codigo, concentracao):
        if codigo in self.iqarTable and concentracao:
            for i, r in enumerate(self.iqarTable[codigo]):
                if int(concentracao) in r:
                    indiceRange = self.iqarTable["indice"][i]
                    iIni = indiceRange[0]
                    iFin = indiceRange[-1]
                    cIni = r[0]
                    cFin = r[-1]
                    return self.iqarTable["qualidadeAr"][i], round(iIni + (((iFin - iIni) / (cFin - cIni)) * (concentracao - cIni)))
        return None, None

    def calc_from_medicao_poluente(self, medicaoPoluente: MedicaoPoluente):
        return self.calc(medicaoPoluente.poluente.codigo, medicaoPoluente.concentracao)

    def calc_from_medicao(self, medicao: Medicao):
        calcs = []
        for mp in medicao.medicaoPoluentes:
            qualidadeAr, iqar = self.calc_from_medicao_poluente(mp)
            if qualidadeAr and iqar:
                calcs.append({"poluente": mp.poluente.codigo,
                              "qualidadeAr": qualidadeAr,
                              "iqar": iqar})
        calc = max(calcs, key=lambda calc: calc["iqar"])
        return calc["poluente"], calc["qualidadeAr"], calc["iqar"]
