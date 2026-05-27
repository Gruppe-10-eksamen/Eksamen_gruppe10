"""
Contract Service — FastAPI entrypoint.

Ved opstart oprettes databasetabellerne (til MVP-formål; i produktion ville man
bruge migrationsværktøjet Alembic). /health bruges til overvågning.
"""
import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import Base, engine
from app.infrastructure import models  # noqa: F401 (registrerer modeller på Base)
from app.api.routes import contracts

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("contract-service")

app = FastAPI(title="Arla RoW DS — Contract Service", version="1.0.0")
Instrumentator().instrument(app).expose(app)
app.include_router(contracts.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Contract Service startet — tabeller sikret.")


@app.get("/health", tags=["ops"])
def health():
    """Health check til overvågning og CI/CD."""
    return {"status": "ok", "service": "contract-service"}
