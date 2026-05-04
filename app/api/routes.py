import hashlib

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.connection import get_database
from app.models.document import DocumentoCrear, DocumentoRespuesta
from app.services import document_service
from app.services.pdf_service import es_duplicado, extraer_texto, validar_pdf

router = APIRouter(prefix="/documentos", tags=["documentos"])


def db_dep() -> AsyncIOMotorDatabase:
    return get_database()


@router.post("/", response_model=DocumentoRespuesta, status_code=201)
async def subir_pdf(
    archivo: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    contenido = await archivo.read()

    # Validar formato y tamaño
    try:
        validar_pdf(contenido, archivo.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Calcular checksum y verificar duplicados
    checksum = hashlib.sha256(contenido).hexdigest()
    checksums_existentes = await document_service.obtener_checksums(db)
    if es_duplicado(checksum, checksums_existentes):
        raise HTTPException(status_code=409, detail="El documento ya existe")

    # Extraer texto y guardar
    texto = extraer_texto(contenido)
    datos = DocumentoCrear(
        nombre=archivo.filename,
        texto=texto,
        checksum=checksum,
    )
    return await document_service.guardar_documento(db, datos)


@router.get("/", response_model=list[DocumentoRespuesta])
async def listar(db: AsyncIOMotorDatabase = Depends(db_dep)):
    return await document_service.listar_documentos(db)


@router.get("/{documento_id}", response_model=DocumentoRespuesta)
async def obtener(
    documento_id: str,
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    doc = await document_service.obtener_documento(db, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return doc


@router.delete("/{documento_id}", status_code=204)
async def eliminar(
    documento_id: str,
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    eliminado = await document_service.eliminar_documento(db, documento_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Documento no encontrado")