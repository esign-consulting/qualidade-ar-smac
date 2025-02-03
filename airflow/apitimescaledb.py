import psycopg2


class TimescaleDB:

    def __init__(self,
                 host="localhost",
                 port=5432,
                 username="postgres",
                 password="S3cr3t",
                 dbname="postgres"):
        self.conn = psycopg2.connect(f"postgres://{username}:{password}@{host}:{port}/{dbname}?sslmode=require")

    def init_estacoes_table(self):
        query_create_sensors_table = """C
            REATE TABLE estacoes (
                codigo SERIAL PRIMARY KEY,
                nome VARCHAR(50),
                location VARCHAR(50)
            );
        """