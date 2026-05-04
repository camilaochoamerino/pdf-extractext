import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.models.document import DocumentoCrear
from app.services import document_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc_mongo(nombre="archivo.pdf", texto="Hola", checksum="abc123"):
    """Simula un documento tal como lo devuelve MongoDB."""
    from bson import ObjectId
    return {
        "_id": ObjectId(),
        "nombre": nombre,
        "texto": texto,
        "checksum": checksum,
        "fecha_subida": datetime.now(timezone.utc),
    }


def _mock_db(docs: list[dict] | None = None):
    """Crea un mock de AsyncIOMotorDatabase con una colección configurable."""
    docs = docs or []

    coleccion = MagicMock()

    # find() → cursor async iterable
    async def _aiter_docs(*args, **kwargs):
        for d in docs:
            yield d

    coleccion.find = MagicMock(return_value=_aiter_docs())

    # find_one()
    coleccion.find_one = AsyncMock(return_value=docs[0] if docs else None)

    # insert_one()
    from bson import ObjectId
    insert_result = MagicMock()
    insert_result.inserted_id = ObjectId()
    coleccion.insert_one = AsyncMock(return_value=insert_result)

    # delete_one()
    delete_result = MagicMock()
    delete_result.deleted_count = 1
    coleccion.delete_one = AsyncMock(return_value=delete_result)

    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=coleccion)
    return db, coleccion


# ---------------------------------------------------------------------------
# obtener_checksums
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_obtener_checksums_devuelve_lista():
    docs = [
        {"_id": "x", "checksum": "abc"},
        {"_id": "y", "checksum": "def"},
    ]
    coleccion = MagicMock()

    async def _aiter(*a, **kw):
        for d in docs:
            yield d

    coleccion.find = MagicMock(return_value=_aiter())
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=coleccion)

    resultado = await document_service.obtener_checksums(db)
    assert resultado == ["abc", "def"]


@pytest.mark.asyncio
async def test_obtener_checksums_vacio():
    coleccion = MagicMock()

    async def _aiter(*a, **kw):
        return
        yield  # hace que sea un async generator

    coleccion.find = MagicMock(return_value=_aiter())
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=coleccion)

    resultado = await document_service.obtener_checksums(db)
    assert resultado == []


# ---------------------------------------------------------------------------
# guardar_documento
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_guardar_documento_retorna_respuesta():
    doc_guardado = _doc_mongo()
    db, col = _mock_db([doc_guardado])
    # find_one devuelve el doc después del insert
    col.find_one = AsyncMock(return_value=doc_guardado)

    datos = DocumentoCrear(
        nombre="archivo.pdf",
        texto="Contenido del PDF",
        checksum="abc123",
    )
    resultado = await document_service.guardar_documento(db, datos)

    assert resultado.nombre == "archivo.pdf"
    assert resultado.checksum == "abc123"
    col.insert_one.assert_called_once()


# ---------------------------------------------------------------------------
# listar_documentos
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_documentos_retorna_lista():
    docs = [_doc_mongo("a.pdf", "texto a", "aaa"), _doc_mongo("b.pdf", "texto b", "bbb")]
    coleccion = MagicMock()

    async def _aiter(*a, **kw):
        for d in docs:
            yield d

    coleccion.find = MagicMock(return_value=_aiter())
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=coleccion)

    resultado = await document_service.listar_documentos(db)
    assert len(resultado) == 2
    assert resultado[0].nombre == "a.pdf"
    assert resultado[1].nombre == "b.pdf"


# ---------------------------------------------------------------------------
# obtener_documento
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_obtener_documento_existente():
    from bson import ObjectId
    oid = ObjectId()
    doc = _doc_mongo()
    doc["_id"] = oid

    db, col = _mock_db([doc])
    col.find_one = AsyncMock(return_value=doc)

    resultado = await document_service.obtener_documento(db, str(oid))
    assert resultado is not None
    assert resultado.id == str(oid)


@pytest.mark.asyncio
async def test_obtener_documento_no_existe():
    db, col = _mock_db()
    col.find_one = AsyncMock(return_value=None)

    from bson import ObjectId
    resultado = await document_service.obtener_documento(db, str(ObjectId()))
    assert resultado is None


@pytest.mark.asyncio
async def test_obtener_documento_id_invalido():
    db, _ = _mock_db()
    resultado = await document_service.obtener_documento(db, "id-no-valido")
    assert resultado is None


# ---------------------------------------------------------------------------
# eliminar_documento
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_eliminar_documento_existente():
    from bson import ObjectId
    db, col = _mock_db()
    resultado = await document_service.eliminar_documento(db, str(ObjectId()))
    assert resultado is True
    col.delete_one.assert_called_once()


@pytest.mark.asyncio
async def test_eliminar_documento_no_existe():
    from bson import ObjectId
    db, col = _mock_db()
    col.delete_one.return_value = MagicMock(deleted_count=0)
    col.delete_one = AsyncMock(return_value=MagicMock(deleted_count=0))

    resultado = await document_service.eliminar_documento(db, str(ObjectId()))
    assert resultado is False


@pytest.mark.asyncio
async def test_eliminar_documento_id_invalido():
    db, _ = _mock_db()
    resultado = await document_service.eliminar_documento(db, "id-no-valido")
    assert resultado is False