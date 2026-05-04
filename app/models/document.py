from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DocumentoBase(BaseModel):
    nombre: str
    texto: str
    checksum: str


class DocumentoCrear(DocumentoBase):
    pass


class Documento(DocumentoBase):
    id: str = Field(alias="_id")
    fecha_subida: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}


class DocumentoRespuesta(DocumentoBase):
    id: str
    fecha_subida: datetime