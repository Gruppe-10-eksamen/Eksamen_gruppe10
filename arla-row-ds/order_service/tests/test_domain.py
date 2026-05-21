"""Unit tests af Order-aggregatet og dets livscyklus-regler."""
from datetime import date

import pytest

from app.domain.aggregates import Order, OrderLine
from app.domain.value_objects import Channel, Quantity, OrderStatus


def _make_order():
    order = Order("ORD-1", "DIST-001", Channel.EMAIL, date(2026, 1, 15))
    order.add_line(OrderLine("OL-1", "ARLA-MILK-1L", Quantity(60)))
    return order


def test_new_order_is_received():
    assert _make_order().status == OrderStatus.RECEIVED


def test_validate_sets_prices_and_total():
    order = _make_order()
    order.validate({"ARLA-MILK-1L": 9.0})
    assert order.status == OrderStatus.VALIDATED
    assert order.total_value == 540.0  # 60 * 9.0


def test_reject_sets_reason():
    order = _make_order()
    order.reject("Produkt ikke tilladt")
    assert order.status == OrderStatus.REJECTED
    assert order.rejection_reason == "Produkt ikke tilladt"


def test_cannot_validate_twice():
    order = _make_order()
    order.validate({"ARLA-MILK-1L": 9.0})
    with pytest.raises(ValueError):
        order.validate({"ARLA-MILK-1L": 9.0})


def test_negative_quantity_rejected():
    with pytest.raises(ValueError):
        Quantity(-5)


def test_events_are_emitted():
    order = _make_order()
    order.register_received()
    order.validate({"ARLA-MILK-1L": 9.0})
    events = order.pull_events()
    names = [type(e).__name__ for e in events]
    assert "OrderReceived" in names
    assert "OrderValidated" in names
