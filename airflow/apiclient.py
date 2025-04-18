import datetime
import json
import logging
import requests
import time


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Poluente):
            return obj.poluente
        elif isinstance(obj, datetime.date):
            return obj.strftime("%d/%m/%Y")
        return vars(obj)


class MedicaoPoluente:

    def __init__(self, poluente, concentracao):
        if isinstance(poluente, str):
            self.poluente = Poluente(poluente)
        elif isinstance(poluente, Poluente):
            self.poluente = poluente
        else:
            raise TypeError(f"Invalid type {type(poluente)} for Poluente.")

        if isinstance(concentracao, str):
            try:
                self.concentracao = float(concentracao.replace(',', '.'))
            except ValueError:
                self.concentracao = None
        elif isinstance(concentracao, (int, float)):
            self.concentracao = concentracao
        else:
            raise TypeError(f"Invalid type {type(concentracao)} for concentracao.")
        

    def __str__(self):
        return json.dumps(vars(self), cls=CustomEncoder, ensure_ascii=False)

    def __repr__(self):
        return str(self)


class Estacao:

    def __init__(self, nome, codigo, latitude, longitude):
        self.nome = nome
        self.codigo = codigo
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return json.dumps(vars(self), ensure_ascii=False)

    def __repr__(self):
        return str(self)

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

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Poluente) and self.codigo == other.codigo

    def __hash__(self):
        return hash(f"Poluente {self.codigo}")


class Medicao:

    def __init__(self, estacao, classificacao, indice, poluente, medicaoPoluentes):
        if isinstance(estacao, dict):
            self.estacao = Estacao(**estacao)
        elif isinstance(estacao, Estacao):
            self.estacao = estacao
        else:
            raise TypeError(f"Invalid type {type(estacao)} for Estacao.")
        
        self.classificacao = classificacao

        if isinstance(indice, str):
            try:
                self.indice = float(indice.replace(',', '.'))
            except ValueError:
                self.indice = None
        elif isinstance(indice, (int, float)):
            self.indice = indice
        else:
            raise TypeError(f"Invalid type {type(indice)} for indice.")

        if isinstance(poluente, str):
            self.poluente = Poluente(poluente)
        elif isinstance(poluente, Poluente):
            self.poluente = poluente
        else:
            raise TypeError(f"Invalid type {type(poluente)} for Poluente.")

        self.medicaoPoluentes = []
        for mp in medicaoPoluentes:
            if isinstance(mp, dict):
                self.medicaoPoluentes.append(MedicaoPoluente(**mp))
            elif isinstance(mp, MedicaoPoluente):
                self.medicaoPoluentes.append(mp)
            else:
                raise TypeError(f"Invalid type {type(mp)} for MedicaoPoluente.")

    @property
    def poluentes(self) -> list[Poluente]:
        return [mp.poluente for mp in self.medicaoPoluentes
                if self.get_concentracao_poluente(mp.poluente.codigo)]

    def get_concentracao_poluente(self, codigo_poluente: str) -> float:
        medicao_poluente = next((mp for mp in self.medicaoPoluentes
                                 if codigo_poluente == mp.poluente.codigo), None)
        return medicao_poluente.concentracao if medicao_poluente else None

    def is_valid(self, data: datetime.date, iqar_tolerance: int = 0) -> bool:
        iqar_calculator = IQArCalculator()
        calculated = iqar_calculator.calc_from_medicao(data, self)
        expected = (self.poluente.codigo, self.classificacao, self.indice)
        is_valid = calculated == expected or \
            (calculated[0:1] == expected[0:1] and abs(calculated[2] - expected[2]) <= iqar_tolerance)
        if not is_valid:
            logging.warning(f"Calculated: {calculated}")
            logging.warning(f"Expected: {expected}")
            print(self)
        return is_valid

    def __str__(self):
        return json.dumps(vars(self), cls=CustomEncoder, ensure_ascii=False)

    def __repr__(self):
        return str(self)


class Boletim:

    def __init__(self, data, medicoes):
        if isinstance(data, str):
            try:
                self.data = datetime.datetime.strptime(data.split(" ")[0], "%d/%m/%Y").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {data}")
        elif isinstance(data, datetime.date):
            self.data = data
        else:
            raise TypeError(f"Invalid type {type(data)} for data.")
        self.medicoes = []
        for m in medicoes:
            if isinstance(m, dict):
                self.medicoes.append(Medicao(**m))
            elif isinstance(m, Medicao):
                self.medicoes.append(m)
            else:
                raise TypeError(f"Invalid type {type(m)} for Medicao.")

    @property
    def estacoes(self) -> list[Estacao]:
        return [m.estacao for m in self.medicoes]
    
    @property
    def poluentes(self) -> list[Poluente]:
        poluentes = []
        for m in self.medicoes:
            poluentes = list(set(poluentes + m.poluentes))
        return poluentes

    def is_valid(self, iqar_tolerance: int = 0) -> bool:
        for m in self.medicoes:
            if not m.is_valid(self.data, iqar_tolerance):
                return False
        return True

    def __str__(self):
        return json.dumps(vars(self), cls=CustomEncoder, ensure_ascii=False)

    def __repr__(self):
        return str(self)


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



class IQArCalculator:

    def __init__(self):
        self.old_iqar_table = {
            "qualidadeAr": ["Boa", "Regular", "Inadequada", "Má", "Péssima"],
            "indice": [range(0, 51), range(51, 101), range(101, 200), range(200, 300), range(300, 401)],
            "MP10": [range(0, 51), range(51, 151), range(151, 251), range(251, 421), range(421, 501)],
            "O3": [range(0, 81), range(81, 161), range(161, 201), range(201, 801), range(801, 1001)],
            "CO": [[n / 10 for n in range(0, 41)], [n / 10 for n in range(41, 91)], [n / 10 for n in range(91, 151)], [n / 10 for n in range(151, 301)], [n / 10 for n in range(301, 401)]],
            "NO2": [range(0, 101), range(101, 321), range(321, 1131), range(1131, 2261), range(2261, 3001)],
            "SO2": [range(0, 81), range(81, 366), range(366, 801), range(801, 1601), range(1601, 2101)]
        }
        self.iqar_table = {
            "qualidadeAr": ["Boa", "Moderada", "Ruim", "Muito ruim", "Péssima"],
            "indice": [range(0, 41), range(41, 81), range(81, 121), range(121, 201), range(201, 401)],
            "MP10": [range(0, 51), range(51, 101), range(101, 151), range(151, 251), range(251, 601)],
            "MP2,5": [range(0, 26), range(26, 51), range(51, 76), range(76, 126), range(126, 301)],
            "O3": [range(0, 101), range(101, 131), range(131, 161), range(161, 201), range(201, 801)],
            "CO": [range(0, 10), range(10, 12), range(12, 14), range(14, 16), range(16, 51)],
            "NO2": [range(0, 201), range(201, 241), range(241, 321), range(321, 1131), range(1131, 3751)],
            "SO2": [range(0, 21), range(21, 41), range(41, 366), range(366, 801), range(801, 2621)]
        }

    def custom_round(self, value):
        if value % 1 < 0.5:
            return int(value)
        elif value % 1 > 0.5:
            return int(value) + 1
        elif value % 1 == 0.5:
            if int(value) % 2 == 0:
                return int(value)
            else:
                return int(value) + 1

    def calc(self, data: datetime.date, codigo: str, concentracao: float) -> tuple[str, float]:
        iqar_table_date = datetime.datetime.strptime("19/11/2019", "%d/%m/%Y").date()
        table = self.iqar_table if data >= iqar_table_date else self.old_iqar_table
        if codigo in table and concentracao:
            rounded_concentracao = self.custom_round(concentracao)
            for i, r in enumerate(table[codigo]):
                if rounded_concentracao in r:
                    indiceRange = table["indice"][i]
                    iIni = indiceRange[0]
                    iFin = indiceRange[-1]
                    cIni = r[0]
                    cFin = r[-1]
                    # print(f"self.custom_round({iIni} + ((({iFin} - {iIni}) / ({cFin} - {cIni})) * ({rounded_concentracao} - {cIni})))")
                    # print(f"self.custom_round({iIni} + (({(iFin - iIni)} / {(cFin - cIni)}) * {(rounded_concentracao - cIni)}))")
                    # print(f"self.custom_round({iIni} + ({((iFin - iIni) / (cFin - cIni))} * {(rounded_concentracao - cIni)}))")
                    # print(f"self.custom_round({iIni} + {(((iFin - iIni) / (cFin - cIni)) * (rounded_concentracao - cIni))})")
                    # print(f"self.custom_round({iIni + (((iFin - iIni) / (cFin - cIni)) * (rounded_concentracao - cIni))})")
                    # print(f"{self.custom_round(iIni + (((iFin - iIni) / (cFin - cIni)) * (rounded_concentracao - cIni)))}")
                    return table["qualidadeAr"][i], self.custom_round(iIni + (((iFin - iIni) / (cFin - cIni)) * (rounded_concentracao - cIni)))
        return None, None

    def calc_from_medicao_poluente(self, data: datetime.date, medicaoPoluente: MedicaoPoluente) -> tuple[str, float]:
        return self.calc(data, medicaoPoluente.poluente.codigo, medicaoPoluente.concentracao)

    def calc_from_medicao(self, data: datetime.date, medicao: Medicao) -> tuple[str, str, float]:
        calcs = []
        for mp in medicao.medicaoPoluentes:
            qualidadeAr, iqar = self.calc_from_medicao_poluente(data, mp)
            if qualidadeAr and iqar is not None:
                calcs.append({"poluente": mp.poluente.codigo,
                              "qualidadeAr": qualidadeAr,
                              "iqar": iqar})
        calc = max(calcs, key=lambda calc: calc["iqar"])
        return calc["poluente"], calc["qualidadeAr"], calc["iqar"]
