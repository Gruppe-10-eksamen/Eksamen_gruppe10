"""
Order Service — FastAPI entrypoint.

Samler routes for ordrer og forecast. Opretter tabeller ved opstart (MVP).
/health bruges til overvågning og af CI/CD til at verificere at servicen kører.
"""
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import Base, engine
from app.logging_config import configure_logging
from app.infrastructure import models  # noqa: F401
from app.api.routes import orders, forecast

logger = configure_logging()

app = FastAPI(title="Arla RoW DS — Order Service", version="1.0.0")
Instrumentator().instrument(app).expose(app)
app.include_router(orders.router)
app.include_router(forecast.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Order Service startet — tabeller sikret.")


@app.get("/health", tags=["ops"])
def health():
    return {"status": "ok", "service": "order-service"}
