"""Unit test af analytics domain service."""
from datetime import date

from app.domain.aggregates import Order, OrderLine
from app.domain.value_objects import Channel, Quantity
from app.domain.services import DemandForecastService


def _order(qty, day):
    o = Order(f"ORD-{day}", "DIST-001", Channel.API, date(2026, 1, day))
    o.add_line(OrderLine(f"OL-{day}", "ARLA-MILK-1L", Quantity(qty)))
    o.validate({"ARLA-MILK-1L": 9.0})
    return o


def test_forecast_increasing_trend():
    # Stigende mængder -> forecast bør være >= sidste observation
    orders = [_order(10, 1), _order(20, 2), _order(30, 3)]
    result = DemandForecastService().forecast_for_distributor(orders)
    assert result.forecast_next_period >= 30
    assert result.historical_periods == 3
    assert result.total_historical_quantity == 60


def test_forecast_empty_returns_none():
    assert DemandForecastService().forecast_for_distributor([]) is None
