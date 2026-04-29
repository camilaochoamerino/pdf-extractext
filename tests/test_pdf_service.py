import pytest
from app.services.pdf_service import extraer_texto, validar_pdf, es_duplicado


def test_extraer_texto_devuelve_string():
    with open("tests/sample.pdf", "rb") as f:
        pdf_bytes = f.read()
    resultado = extraer_texto(pdf_bytes)
    assert isinstance(resultado, str)
    assert len(resultado) > 0


def test_validar_pdf_formato_incorrecto():
    with pytest.raises(ValueError, match="debe ser un PDF"):
        validar_pdf(b"contenido cualquiera", "image/png")


def test_validar_pdf_tamanio_excedido():
    pdf_grande = b"a" * (11 * 1024 * 1024)
    with pytest.raises(ValueError, match="supera los"):
        validar_pdf(pdf_grande, "application/pdf")


def test_validar_pdf_correcto():
    with open("tests/sample.pdf", "rb") as f:
        contenido = f.read()
    validar_pdf(contenido, "application/pdf")


def test_detecta_duplicado():
    checksums = ["abc123", "def456", "ghi789"]
    assert es_duplicado("abc123", checksums) is True


def test_no_es_duplicado():
    checksums = ["abc123", "def456", "ghi789"]
    assert es_duplicado("xyz999", checksums) is False


def test_lista_vacia_no_es_duplicado():
    assert es_duplicado("abc123", []) is False