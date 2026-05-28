"""Pydantic-schemas: API-kontrakten for Order Service."""
from datetime import date

from pydantic import BaseModel, Field


class OrderLineIn(BaseModel):
    product_code: str
    quantity: int = Field(gt=0, description="Skal være positiv")
    unit: str = "units"


class OrderIn(BaseModel):
    """Indgående ordre — dette er en 'IncomingOrder' før validering."""
    distributor_id: str
    channel: str = Field(description="EMAIL, WHATSAPP, TEAMS, SMS eller API")
    order_date: date
    lines: list[OrderLineIn]


class OrderLineOut(BaseModel):
    product_code: str
    quantity: int
    unit_price: float | None
    line_total: float


class OrderOut(BaseModel):
    order_id: str
    distributor_id: str
    channel: str
    order_date: date
    status: str
    rejection_reason: str | None
    total_value: float
    total_quantity: int
    sap_order_id: str | None = None
    lines: list[OrderLineOut]


class ProductForecastOut(BaseModel):
    product_code: str
    total_historical_quantity: int
    forecast_next_period: float


class ForecastOut(BaseModel):
    distributor_id: str
    historical_periods: int
    total_historical_quantity: int
    rejection_rate: float
    forecast_next_period: float
    products: list[ProductForecastOut] = []