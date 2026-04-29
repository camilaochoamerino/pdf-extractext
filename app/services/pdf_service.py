import pdfplumber
import io


def extraer_texto(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        paginas = [pagina.extract_text() or "" for pagina in pdf.pages]
    return "\n".join(paginas).strip()
MAX_SIZE_MB = 10
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


def validar_pdf(contenido: bytes, content_type: str) -> None:
    if content_type != "application/pdf":
        raise ValueError("El archivo debe ser un PDF")
    if len(contenido) > MAX_SIZE_BYTES:
        raise ValueError(f"El archivo supera los {MAX_SIZE_MB}MB permitidos")