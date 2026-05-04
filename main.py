from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.connection import cerrar_conexion


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: la conexión se crea al primer uso (lazy)
    yield
    # Shutdown: cerrar conexión limpiamente
    await cerrar_conexion()


app = FastAPI(
    title="PDF ExtracText",
    description="Sube PDFs, extrae su texto y gestiona documentos",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)

def main():
    print("Este es PDF-EXTRACTEXT")

if __name__ == "__main__":
    main()