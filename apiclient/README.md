# qarsmac

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pypi](https://img.shields.io/pypi/v/qarsmac.svg)](https://pypi.org/project/qarsmac)
[![versions](https://img.shields.io/pypi/pyversions/qarsmac.svg)](https://pypi.org/project/qarsmac)

Cliente Python da API de Qualidade do Ar da SMAC.

## Uso

```python
from qarsmac.requestor import BoletimRequestor

requestor = BoletimRequestor("https://qualidadearsmac.azurewebsites.net/api")
boletim = requestor.request()
print(boletim)
```
