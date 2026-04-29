import pytest
from app.services.pdf_service import extraer_texto


def test_extraer_texto_devuelve_string():
    with open("tests/sample.pdf", "rb") as f:
        pdf_bytes = f.read()
    resultado = extraer_texto(pdf_bytes)
    assert isinstance(resultado, str)
    assert len(resultado) > 0