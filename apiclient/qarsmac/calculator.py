import datetime
from qarsmac.model import Medicao, MedicaoPoluente


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
