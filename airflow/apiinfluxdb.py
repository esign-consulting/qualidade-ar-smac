from apiclient import Boletim, MedicaoPoluente
from datetime import datetime
from influxdb_client import InfluxDBClient, Point


class InfluxDB:

    def __init__(self,
                 url="http://localhost:8086",
                 org="esign-consulting",
                 token="my-super-secret-auth-token"):
        self.client = InfluxDBClient(url=url, org=org, token=token)

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
    
    def get_last_timestamp(self) -> datetime:
        query_api = self.client.query_api()
        query = 'from(bucket: "qualidadear-diaria") \
            |> range(start: 0, stop: now()) \
            |> filter(fn: (r) => r._measurement == "IQAR" and r.orgao == "SMAC") \
            |> keep(columns: ["_time"]) \
            |> sort(columns: ["_time"], desc: false) \
            |> last(column: "_time")'
        last_data = query_api.query(query)
        return last_data[0].records[0]["_time"]
    
    def write_boletim(self, boletim: Boletim):
        write_api = self.client.write_api()
        write_api.write(bucket="qualidadear-diaria",
                        record=self.convert_boletim_to_points_array(boletim))
