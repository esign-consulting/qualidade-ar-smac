#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apidocker import SMAC

import datetime
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

smac = SMAC()
port = smac.run()
requestor = BoletimRequestor(f"http://localhost:{port}/smac")

today = datetime.date.today()
d_string = today.strftime("%d/%m/%Y")
boletim = requestor.request(d_string)
if boletim:
    for estacao in boletim.estacoes:
        logging.info(f"{estacao.codigo} - {estacao.nome}")

smac.stop()
