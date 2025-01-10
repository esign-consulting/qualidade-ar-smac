#!/usr/bin/env python3

from apiclient import BoletimRequestor
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

requestor = BoletimRequestor("http://www.esign.com.br:13887/smac")
boletim = requestor.request()

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
