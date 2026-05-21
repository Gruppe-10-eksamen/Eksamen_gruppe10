"""
Forecast endpoint — eksponerer analytics domain service.

GET /forecast/{distributor_id}
    Henter distributørens historiske ordrer fra databasen og kører
    DemandForecastService for at producere deskriptiv, diagnostisk og
    predictiv indsigt.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_api_key
from app.domain.services.demand_forecast_service import DemandForecastService
from app.infrastructure.repositories import OrderRepository
from app.api.schemas import ForecastOut

router = APIRouter(prefix="/forecast", tags=["analytics"])


@router.get("/{distributor_id}", response_model=ForecastOut)
def forecast(distributor_id: str, db: Session = Depends(get_db), _=Depends(require_api_key)):
    repo = OrderRepository(db)
    all_orders = repo.list_all()
    distributor_orders = sorted(
        [o for o in all_orders if o.distributor_id == distributor_id],
        key=lambda o: o.order_date,
    )
    if not distributor_orders:
        raise HTTPException(404, f"Ingen ordrer fundet for distributør {distributor_id}")

    result = DemandForecastService().forecast_for_distributor(distributor_orders)
    return ForecastOut(
        distributor_id=result.distributor_id,
        historical_periods=result.historical_periods,
        total_historical_quantity=result.total_historical_quantity,
        rejection_rate=result.rejection_rate,
        forecast_next_period=result.forecast_next_period,
    )
