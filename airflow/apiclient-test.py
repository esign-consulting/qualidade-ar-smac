#!/usr/bin/env python3

from apiclient import Boletim, BoletimRequestor, IQArCalculator

import datetime
import json
import pytest


@pytest.mark.skip(reason="temporarily disabled")
def test_api_requestor():
    requestor = BoletimRequestor("http://www.esign.com.br:13887/smac")
    boletim = requestor.request()

    assert boletim
    assert len(boletim.estacoes) > 0
    assert next((e for e in boletim.estacoes if e.nome == "Centro"), None)


def test_boletim_parse():
    with open('src/test/resources/boletim.json') as f:
        boletim = Boletim(**json.load(f))

        assert boletim.data.strftime("%d/%m/%Y") == "26/12/2024"
        assert len(boletim.estacoes) == 7
        assert len(boletim.poluentes) == 6
        medicao = next((m for m in boletim.medicoes if m.estacao.nome == "Centro"), None)
        assert medicao.classificacao == "Boa"
        assert medicao.poluente.codigo == "O3"
        assert [p.codigo for p in medicao.poluentes] == ["O3", "CO"] 
        assert len(medicao.medicaoPoluentes) == 6
        medicao_poluente = next((mp for mp in medicao.medicaoPoluentes if mp.poluente.codigo == "O3"), None)
        assert medicao_poluente.concentracao == 29
        assert medicao_poluente.poluente.unidade_concentracao == "µg/m³"

def test_iqar_calculator():
    iqar_calculator = IQArCalculator()
    today = datetime.date.today()
    # assert iqar_calculator.calc(today, "MP10", 38.0) == ("Boa", 29)
    assert iqar_calculator.calc(today, "MP10", 210) == ("Muito ruim", 168)
    assert iqar_calculator.calc(today, "O3", 135) == ("Ruim", 86)
    assert iqar_calculator.calc(today, "NO2", 220) == ("Moderada", 60)

    with open('src/test/resources/boletim.json') as f:
        boletim = Boletim(**json.load(f))
        assert boletim.is_valid()
