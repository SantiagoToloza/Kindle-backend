from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.articles import router as articles_router
from app.api.kindle import router as kindle_router
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas si no existen (en producción preferís Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Kindle Reader API",
    description="Backend para enviar artículos a la Kindle via browser",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustar en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles_router)
app.include_router(kindle_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
