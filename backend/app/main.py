from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import ingredients, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas si no existen (alternativa a Alembic en dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API para generación de recetas con IA basada en inventario de ingredientes.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredients.router, prefix="/api/ingredients",  tags=["Ingredientes"])
app.include_router(recipes.router,     prefix="/api/recipes",      tags=["Recetas"])


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
