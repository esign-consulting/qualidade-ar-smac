from apiclient import Boletim, Estacao, MedicaoPoluente
from datetime import datetime
from influxdb_client_3 import Point


class InfluxDB:

    def __init__(self):
        pass

    def get_concentracao(self, medicao_poluente: MedicaoPoluente) -> float:
        if medicao_poluente:
            try:
                return float(medicao_poluente.concentracao.replace(',', '.'))
            except ValueError:
                return None
        return None
    
    def convert_boletim_to_points_array(self, boletim: Boletim) -> list[Point]:
        points_array = []
        ts = int(datetime.timestamp(datetime.combine(
            datetime.strptime(boletim.data, "%d/%m/%Y").date(),
            datetime.min.time())) * 1000000000)
        for medicao in boletim.medicoes:
            points_array.append(Point("IQAR")
                               .tag("estado", "RJ")
                               .tag("cidade", "Rio de Janeiro")
                               .tag("orgao", "SMAC")
                               .tag("estacao", medicao.estacao.nome)
                               .tag("latitude", medicao.estacao.latitude)
                               .tag("longitude", medicao.estacao.longitude)
                               .tag("poluente", medicao.poluente)
                               .tag("classificacao", medicao.classificacao)
                               .field("value", float(medicao.indice.replace(',', '.')))
                               .time(ts))
            for poluente in ["MP10", "MP2,5", "O3", "CO", "NO2", "SO2"]:
                medicao_poluente = next((mp for mp in medicao.medicaoPoluentes if poluente in mp.poluente), None)
                concentracao = self.get_concentracao(medicao_poluente)
                if medicao_poluente and concentracao:
                    points_array.append(Point(poluente.replace(',', '.'))
                                       .tag("estado", "RJ")
                                       .tag("cidade", "Rio de Janeiro")
                                       .tag("orgao", "SMAC")
                                       .tag("estacao", medicao.estacao.nome)
                                       .tag("latitude", medicao.estacao.latitude)
                                       .tag("longitude", medicao.estacao.longitude)
                                       .field("value", concentracao)
                                       .time(ts))
        return points_array
