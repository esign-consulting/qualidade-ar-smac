# qarsmac

Cliente Python da API de Qualidade do Ar da SMAC.

## Uso

```python
from qarsmac.requestor import BoletimRequestor

requestor = BoletimRequestor("https://qualidadearsmac.azurewebsites.net/api")
boletim = requestor.request()
print(boletim)
```
