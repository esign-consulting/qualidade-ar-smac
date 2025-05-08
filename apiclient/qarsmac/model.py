import datetime
import json


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

    def __str__(self):
        return json.dumps(vars(self), cls=CustomEncoder, ensure_ascii=False)

    def __repr__(self):
        return str(self)
