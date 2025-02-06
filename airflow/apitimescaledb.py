from apiclient import Boletim, Medicao
from datetime import datetime

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

    def insert_boletim(self, boletim: Boletim):
        estacoes_table = EstacoesTable()
        estacoes_table.create(self.conn)
        logging.info("Estacoes table OK.")
        estacoes_table.upsert_estacoes(self.conn, boletim)
        logging.info("Estacoes loaded into table.")

        medicoes_table = MedicoesTable()
        medicoes_table.create(self.conn)
        logging.info("Medicoes table OK.")
        medicoes_table.upsert_medicoes(self.conn, boletim)
        logging.info("Medicoes loaded into table.")


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


class MedicoesTable():

    def __init__(self):
        self.create_table_command = """
            CREATE TABLE IF NOT EXISTS medicoes (
                data DATE NOT NULL,
                codigo_estacao VARCHAR(2),
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
        self.create_hypertable_command = "SELECT create_hypertable('medicoes', by_range('data'));"
        self.upsert_command = """
            INSERT INTO medicoes (data, codigo_estacao, MP10, MP2_5, O3, CO, NO2, SO2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT(data, codigo_estacao)
            DO UPDATE SET
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
                        self.get_concentracao_poluente(medicao, "MP10"),
                        self.get_concentracao_poluente(medicao, "MP2,5"),
                        self.get_concentracao_poluente(medicao, "O3"),
                        self.get_concentracao_poluente(medicao, "CO"),
                        self.get_concentracao_poluente(medicao, "NO2"),
                        self.get_concentracao_poluente(medicao, "SO2"))
                cursor.execute(self.upsert_command, data)
            except (Exception, psycopg2.Error) as error:
                logging.error(error.pgerror)
        conn.commit()
        cursor.close()

    def get_concentracao_poluente(self, medicao: Medicao, poluente: str):
        medicao_poluente = next((mp for mp in medicao.medicaoPoluentes if poluente in mp.poluente), None)
        if medicao_poluente:
            try:
                return float(medicao_poluente.concentracao.replace(',', '.'))
            except ValueError:
                return None
        else:
            return None
