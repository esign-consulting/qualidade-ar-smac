#!/usr/bin/env python3

from apiclient import BoletimRequestor

import datetime


def test_apiclient():
    requestor = BoletimRequestor("http://www.esign.com.br:13887/smac")

    today = datetime.date.today()
    d_string = today.strftime("%d/%m/%Y")
    boletim = requestor.request(d_string)

    assert boletim
    assert len(boletim.estacoes) > 0
    assert next((e for e in boletim.estacoes if e.nome == "Centro"), None)
