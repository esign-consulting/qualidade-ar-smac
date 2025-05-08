from qarsmac.model import Boletim, Estacao, Poluente, MedicaoPoluente, Medicao
from datetime import date
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
        self.poluentes_table = PoluentesTable()
        self.medicoes_diarias_table = MedicoesDiariasTable()

    def insert_boletim(self, boletim: Boletim):
        self.estacoes_table.create(self.conn)
        logging.info("estacoes table OK.")
        self.estacoes_table.upsert_estacoes(self.conn, boletim)
        logging.info("Estacoes loaded into table.")

        self.poluentes_table.create(self.conn)
        logging.info("poluentes table OK.")
        self.poluentes_table.upsert_poluentes(self.conn, boletim)
        logging.info("Poluentes loaded into table.")

        self.medicoes_diarias_table.create(self.conn)
        logging.info("medicoes_diarias table OK.")
        self.medicoes_diarias_table.upsert_medicoes(self.conn, boletim)
        logging.info("Medicoes loaded into table.")

    def get_boletim(self, data: date) -> Boletim:
        medicoes = self.medicoes_diarias_table.get_medicoes(self.conn, data)
        return Boletim(data, medicoes)

    def get_first_boletim_data(self) -> date:
        return self.medicoes_diarias_table.get_min_data(self.conn)

    def get_last_boletim_data(self) -> date:
        return self.medicoes_diarias_table.get_max_data(self.conn)

    def get_last_boletim(self) -> Boletim:
        data = self.get_last_boletim_data()
        return self.get_boletim(data)


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
        self.select_command = """
            SELECT codigo, nome, estado, cidade, orgao,
                ST_Y(coordenadas :: geometry) AS "latitude",
                ST_X(coordenadas :: geometry) AS "longitude"
            FROM estacoes;
        """

    def create(self, conn: psycopg2.connect):
        cursor = conn.cursor()
        cursor.execute(self.create_command)
        conn.commit()
        cursor.close()

    def upsert_estacoes(self, conn: psycopg2.connect, boletim: Boletim):
        cursor = conn.cursor()
        for estacao in boletim.estacoes:
            if estacao.codigo:
                try:
                    data = (estacao.codigo, estacao.nome, estacao.longitude, estacao.latitude)
                    cursor.execute(self.upsert_command, data)
                except (Exception, psycopg2.Error) as error:
                    logging.error(error.pgerror)
        conn.commit()
        cursor.close()

    def get_estacoes(self, conn: psycopg2.connect) -> list[Estacao]:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(self.select_command)
        rows = cursor.fetchall()
        cursor.close()

        estacoes = []
        for row in rows:
            estacao = Estacao(row["nome"], row["codigo"], row["latitude"], row["longitude"])
            estacoes.append(estacao)
        return estacoes


class PoluentesTable:

    def __init__(self):
        self.create_command = """
            CREATE TABLE IF NOT EXISTS poluentes (
                codigo VARCHAR(10) PRIMARY KEY,
                nome VARCHAR(50),
                unidade_concentracao VARCHAR(10)
            );
        """
        self.upsert_command = """
            INSERT INTO poluentes (codigo, nome, unidade_concentracao)
            VALUES (%s, %s, %s)
            ON CONFLICT(codigo)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                unidade_concentracao = EXCLUDED.unidade_concentracao;
        """
        self.select_command = """
            SELECT nome || ' (' || codigo || ') [' || unidade_concentracao || ']' AS "poluente"
            FROM poluentes;
        """

    def create(self, conn: psycopg2.connect):
        cursor = conn.cursor()
        cursor.execute(self.create_command)
        conn.commit()
        cursor.close()

    def upsert_poluentes(self, conn: psycopg2.connect, boletim: Boletim):
        cursor = conn.cursor()
        for poluente in boletim.poluentes:
            try:
                data = (poluente.codigo, poluente.nome, poluente.unidade_concentracao)
                cursor.execute(self.upsert_command, data)
            except (Exception, psycopg2.Error) as error:
                logging.error(error.pgerror)
        conn.commit()
        cursor.close()

    def get_poluentes(self, conn: psycopg2.connect) -> list[Poluente]:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(self.select_command)
        rows = cursor.fetchall()
        cursor.close()

        poluentes = []
        for row in rows:
            poluente = Poluente(row["poluente"])
            poluentes.append(poluente)
        return poluentes


class MedicoesDiariasTable():

    def __init__(self):
        self.create_table_command = """
            CREATE TABLE IF NOT EXISTS medicoes_diarias (
                data DATE NOT NULL,
                codigo_estacao VARCHAR(2),
                classificacao VARCHAR(20),
                IQAR INTEGER,
                codigo_poluente VARCHAR(10),
                MP10 DOUBLE PRECISION,
                MP2_5 DOUBLE PRECISION,
                O3 DOUBLE PRECISION,
                CO DOUBLE PRECISION,
                NO2 DOUBLE PRECISION,
                SO2 DOUBLE PRECISION,
                CONSTRAINT medicao_diaria PRIMARY KEY (data, codigo_estacao),
                FOREIGN KEY (codigo_estacao) REFERENCES estacoes (codigo),
                FOREIGN KEY (codigo_poluente) REFERENCES poluentes (codigo)
            );
        """
        self.create_hypertable_command = "SELECT create_hypertable('medicoes_diarias', by_range('data'));"
        self.upsert_command = """
            INSERT INTO medicoes_diarias (data, codigo_estacao, classificacao, IQAR, codigo_poluente, MP10, MP2_5, O3, CO, NO2, SO2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT(data, codigo_estacao)
            DO UPDATE SET
                classificacao = EXCLUDED.classificacao,
                IQAR = EXCLUDED.IQAR,
                codigo_poluente = EXCLUDED.codigo_poluente,
                MP10 = EXCLUDED.MP10,
                MP2_5 = EXCLUDED.MP2_5,
                O3 = EXCLUDED.O3,
                CO = EXCLUDED.CO,
                NO2 = EXCLUDED.NO2,
                SO2 = EXCLUDED.SO2;
        """
        self.select_command = """
            SELECT data, codigo_estacao, classificacao, IQAR, codigo_poluente,
                MP10, MP2_5, O3, CO, NO2, SO2
            FROM medicoes_diarias
            WHERE data = %s;
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
            if medicao.estacao.codigo:
                try:
                    data = (boletim.data,
                            medicao.estacao.codigo,
                            medicao.classificacao,
                            medicao.indice,
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

    def get_min_data(self, conn: psycopg2.connect) -> date:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT min(data) AS min_data FROM medicoes_diarias")
        rows = cursor.fetchall()
        cursor.close()
        return rows[0]["min_data"] if len(rows) == 1 else None

    def get_max_data(self, conn: psycopg2.connect) -> date:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT max(data) AS max_data FROM medicoes_diarias")
        rows = cursor.fetchall()
        cursor.close()
        return rows[0]["max_data"] if len(rows) == 1 else None

    def get_medicoes(self, conn: psycopg2.connect, data: date) -> list[Medicao]:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(self.select_command, (data,))
        rows = cursor.fetchall()
        cursor.close()

        estacoes = EstacoesTable().get_estacoes(conn)
        poluentes = PoluentesTable().get_poluentes(conn)

        medicoes = []
        for row in rows:
            medicaoPoluentes = []
            for col in [("MP10", "mp10"), ("MP2,5", "mp2_5"), ("O3", "o3"), ("CO", "co"), ("NO2", "no2"), ("SO2", "so2")]:
                poluente = next((p for p in poluentes if p.codigo == col[0]), None)
                if poluente and row[col[1]]:
                    medicaoPoluente = MedicaoPoluente(poluente, row[col[1]])
                    medicaoPoluentes.append(medicaoPoluente)

            estacao = next((e for e in estacoes if e.codigo == row["codigo_estacao"]), None)
            poluente = next((p for p in poluentes if p.codigo == row["codigo_poluente"]), None)
            if estacao and poluente:
                medicao = Medicao(estacao, row["classificacao"], row["iqar"], poluente, medicaoPoluentes)
                medicoes.append(medicao)
        return medicoes
