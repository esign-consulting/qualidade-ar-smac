#!/usr/bin/env python3

from apiclient import BoletimRequestor
from apidocker import SMAC

import datetime


def test_apiclient():
    smac = SMAC()
    port = smac.run()
    requestor = BoletimRequestor(f"http://localhost:{port}/smac")

    today = datetime.date.today()
    d_string = today.strftime("%d/%m/%Y")
    boletim = requestor.request(d_string)
    smac.stop()

    assert boletim
    assert len(boletim.estacoes) > 0
    assert next((e for e in boletim.estacoes if e.nome == "Centro"), None)
