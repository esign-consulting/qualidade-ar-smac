import datetime
import logging
from qarsmac.model import Boletim, Medicao
from qarsmac.calculator import IQArCalculator


class BoletimValidator:

    def __init__(self, boletim: Boletim):
        self.boletim = boletim
        self.calculator = IQArCalculator()

    def is_boletim_valid(self, iqar_tolerance: int = 0) -> bool:
        if not self.boletim:
            raise ValueError("Boletim cannot be None or empty")
        for medicao in self.boletim.medicoes:
            if not self.is_medicao_valid(medicao, self.boletim.data, iqar_tolerance):
                return False
        return True

    def is_medicao_valid(self, medicao: Medicao, data: datetime.date, iqar_tolerance: int = 0) -> bool:
        calculated = self.calculator.calc_from_medicao(data, medicao)
        expected = (medicao.poluente.codigo, medicao.classificacao, medicao.indice)
        is_valid = calculated == expected or \
            (calculated[0:1] == expected[0:1] and abs(calculated[2] - expected[2]) <= iqar_tolerance)
        if not is_valid:
            logging.warning(f"Calculated: {calculated}")
            logging.warning(f"Expected: {expected}")
            print(medicao)
        return is_valid
