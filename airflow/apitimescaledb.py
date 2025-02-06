from apiclient import Boletim, Estacao

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
        estacoes_table.upsert_estacoes(self.conn, boletim.estacoes)
        logging.info("Estacoes loaded into table.")


class EstacoesTable:

    def __init__(self):
        self.create_command = """
            CREATE TABLE IF NOT EXISTS estacoes (
                codigo VARCHAR(2) PRIMARY KEY,
                nome VARCHAR(50),
                coordenadas GEOGRAPHY(POINT,4326)
            );
        """
        self.upsert_command = """
            INSERT INTO estacoes (codigo, nome, coordenadas)
            VALUES (%s, %s, 'SRID=4326;POINT(%s %s)')
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

    def upsert_estacoes(self, conn: psycopg2.connect, estacoes: list[Estacao]):
        cursor = conn.cursor()
        for estacao in estacoes:
            try:
                data = (estacao.codigo, estacao.nome, estacao.longitude, estacao.latitude)
                cursor.execute(self.upsert_command, data)
            except (Exception, psycopg2.Error) as error:
                logging.error(error.pgerror)
        conn.commit()
        cursor.close()
