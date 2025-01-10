#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apidocker import SMAC

import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

smac = SMAC()
port = smac.run()
requestor = BoletimRequestor(f"http://localhost:{port}/smac")
boletim = requestor.request()
smac.stop()

if boletim:
    print(boletim.data)
    print(boletim.medicoes[0].estacao.nome)
    print(boletim.medicoes[0].estacao.latitude)
    print(boletim.medicoes[0].estacao.longitude)
    print(boletim.medicoes[0].classificacao)
    print(boletim.medicoes[0].indice)
    print(boletim.medicoes[0].poluente)
    print(boletim.medicoes[0].medicaoPoluentes[1].poluente)
    print(boletim.medicoes[0].medicaoPoluentes[1].concentracao)
