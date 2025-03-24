from apiclient import Boletim
from datetime import datetime, date
from psycopg2 import extras

import logging
import psycopg2

class TimescaleDB:

    def __init__(self,
                 host="localhost",
                 port=5432,
                 username="postgres",
                 password="SuperSecret",
                 dbname="postgres"):
        self.conn = psycopg2.connect(f"postgres://{username}:{password}@{host}:{port}/{dbname}")
        self.estacoes_table = EstacoesTable()
        self.medicoes_diarias_table = MedicoesDiariasTable()

    def insert_boletim(self, boletim: Boletim):
        self.estacoes_table.create(self.conn)
        logging.info("estacoes table OK.")
        self.estacoes_table.upsert_estacoes(self.conn, boletim)
        logging.info("Estacoes loaded into table.")

        self.medicoes_diarias_table.create(self.conn)
        logging.info("medicoes_diarias table OK.")
        self.medicoes_diarias_table.upsert_medicoes(self.conn, boletim)
        logging.info("Medicoes loaded into table.")

    def get_last_boletim_data(self) -> date:
        return self.medicoes_diarias_table.get_max_data(self.conn)


class EstacoesTable:

    def __init__(self):
        self.create_command = """
            CREATE TABLE IF NOT EXISTS estacoes (
                codigo VARCHAR(2) PRIMARY KEY,
                nome VARCHAR(50),
                estado VARCHAR(2),
                cidade VARCHAR(50),
                orgao VARCHAR(10),
                coordenadas GEOGRAPHY(POINT,4326)
            );
        """
        self.upsert_command = """
            INSERT INTO estacoes (codigo, nome, estado, cidade, orgao, coordenadas)
            VALUES (%s, %s, 'RJ', 'Rio de Janeiro', 'SMAC', 'SRID=4326;POINT(%s %s)')
            ON CONFLICT(codigo)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                coordenadas = EXCLUDED.coordenadas;
        """

    def create(self, conn: psycopg2.connect):
        cursor = conn.cursor()
        cursor.execute(self.create_command)
        conn.commit()
        cursor.close()

    def upsert_estacoes(self, conn: psycopg2.connect, boletim: Boletim):
        cursor = conn.cursor()
        for estacao in boletim.estacoes:
            try:
                data = (estacao.codigo, estacao.nome, estacao.longitude, estacao.latitude)
                cursor.execute(self.upsert_command, data)
            except (Exception, psycopg2.Error) as error:
                logging.error(error.pgerror)
        conn.commit()
        cursor.close()


class MedicoesDiariasTable():

    def __init__(self):
        self.create_table_command = """
            CREATE TABLE IF NOT EXISTS medicoes_diarias (
                data DATE NOT NULL,
                codigo_estacao VARCHAR(2),
                classificacao VARCHAR(20),
                IQAR DOUBLE PRECISION,
                poluente VARCHAR(10),
                MP10 DOUBLE PRECISION,
                MP2_5 DOUBLE PRECISION,
                O3 DOUBLE PRECISION,
                CO DOUBLE PRECISION,
                NO2 DOUBLE PRECISION,
                SO2 DOUBLE PRECISION,
                CONSTRAINT medicao_diaria PRIMARY KEY (data, codigo_estacao),
                FOREIGN KEY (codigo_estacao) REFERENCES estacoes (codigo)
            );
        """
        self.create_hypertable_command = "SELECT create_hypertable('medicoes_diarias', by_range('data'));"
        self.upsert_command = """
            INSERT INTO medicoes_diarias (data, codigo_estacao, classificacao, IQAR, poluente, MP10, MP2_5, O3, CO, NO2, SO2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT(data, codigo_estacao)
            DO UPDATE SET
                classificacao = EXCLUDED.classificacao,
                IQAR = EXCLUDED.IQAR,
                poluente = EXCLUDED.poluente,
                MP10 = EXCLUDED.MP10,
                MP2_5 = EXCLUDED.MP2_5,
                O3 = EXCLUDED.O3,
                CO = EXCLUDED.CO,
                NO2 = EXCLUDED.NO2,
                SO2 = EXCLUDED.SO2;
        """

    def create(self, conn: psycopg2.connect):
        cursor = conn.cursor()
        cursor.execute(self.create_table_command)
        try:
            cursor.execute(self.create_hypertable_command)
        except psycopg2.DatabaseError as error:
            if "is already a hypertable" in str(error):
                pass
            else:
                raise error
        conn.commit()
        cursor.close()

    def upsert_medicoes(self, conn: psycopg2.connect, boletim: Boletim):
        cursor = conn.cursor()
        for medicao in boletim.medicoes:
            try:
                data = (datetime.strptime(boletim.data, "%d/%m/%Y").date(),
                        medicao.estacao.codigo,
                        medicao.classificacao,
                        medicao.get_IQAR(),
                        medicao.poluente.codigo,
                        medicao.get_concentracao_poluente("MP10"),
                        medicao.get_concentracao_poluente("MP2,5"),
                        medicao.get_concentracao_poluente("O3"),
                        medicao.get_concentracao_poluente("CO"),
                        medicao.get_concentracao_poluente("NO2"),
                        medicao.get_concentracao_poluente("SO2"))
                cursor.execute(self.upsert_command, data)
            except (Exception, psycopg2.Error) as error:
                logging.error(error.pgerror)
        conn.commit()
        cursor.close()

    def get_max_data(self, conn: psycopg2.connect) -> date:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT max(data) AS max_data FROM medicoes_diarias")
        rows = cursor.fetchall()
        cursor.close()
        return rows[0]["max_data"] if len(rows) == 1 else None
