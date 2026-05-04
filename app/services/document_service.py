from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.document import DocumentoCrear, DocumentoRespuesta

COLECCION = "documentos"


def _serializar(doc: dict) -> DocumentoRespuesta:
    return DocumentoRespuesta(
        id=str(doc["_id"]),
        nombre=doc["nombre"],
        texto=doc["texto"],
        checksum=doc["checksum"],
        fecha_subida=doc["fecha_subida"],
    )


async def obtener_checksums(db: AsyncIOMotorDatabase) -> list[str]:
    cursor = db[COLECCION].find({}, {"checksum": 1})
    return [doc["checksum"] async for doc in cursor]


async def guardar_documento(
    db: AsyncIOMotorDatabase, datos: DocumentoCrear
) -> DocumentoRespuesta:
    from datetime import datetime, timezone

    documento = datos.model_dump()
    documento["fecha_subida"] = datetime.now(timezone.utc)

    resultado = await db[COLECCION].insert_one(documento)
    creado = await db[COLECCION].find_one({"_id": resultado.inserted_id})
    return _serializar(creado)


async def listar_documentos(db: AsyncIOMotorDatabase) -> list[DocumentoRespuesta]:
    cursor = db[COLECCION].find()
    return [_serializar(doc) async for doc in cursor]


async def obtener_documento(
    db: AsyncIOMotorDatabase, documento_id: str
) -> DocumentoRespuesta | None:
    try:
        oid = ObjectId(documento_id)
    except InvalidId:
        return None
    doc = await db[COLECCION].find_one({"_id": oid})
    return _serializar(doc) if doc else None


async def eliminar_documento(
    db: AsyncIOMotorDatabase, documento_id: str
) -> bool:
    try:
        oid = ObjectId(documento_id)
    except InvalidId:
        return False
    resultado = await db[COLECCION].delete_one({"_id": oid})
    return resultado.deleted_count == 1