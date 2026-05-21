"""
Unit tests af domænelaget. Disse tester FORRETNINGSREGLER isoleret — ingen
database, ingen API. Det er kernen i en god teststrategi: domænelogikken skal
kunne testes uden infrastruktur.
"""
from datetime import date

import pytest

from app.domain.aggregates import DistributorContract
from app.domain.entities import Distributor, ContractLine
from app.domain.value_objects import (
    MarketRegion, Region, PricingTier, Tier, ContractTerms,
)


def _make_contract():
    distributor = Distributor("DIST-001", "Test Dist",
                              MarketRegion(Region.MENA, "AED"))
    terms = ContractTerms(payment_days=30, minimum_order_quantity=50,
                          valid_from=date(2025, 1, 1), valid_to=date(2026, 12, 31))
    pricing = PricingTier(Tier.STRATEGIC, 0.10)
    contract = DistributorContract("CON-001", distributor, terms, pricing)
    contract.add_contract_line(ContractLine("CL-001", "ARLA-MILK-1L", 10.0, "AED"))
    return contract


def test_price_applies_discount():
    contract = _make_contract()
    # 10.0 med 10% rabat = 9.0
    assert contract.price_for("ARLA-MILK-1L") == 9.0


def test_unknown_product_returns_none():
    contract = _make_contract()
    assert contract.price_for("UKENDT-PRODUKT") is None


def test_duplicate_product_code_rejected():
    contract = _make_contract()
    with pytest.raises(ValueError):
        contract.add_contract_line(ContractLine("CL-002", "ARLA-MILK-1L", 11.0, "AED"))


def test_contract_validity_window():
    contract = _make_contract()
    assert contract.is_valid_on(date(2025, 6, 1)) is True
    assert contract.is_valid_on(date(2030, 1, 1)) is False


def test_invalid_discount_raises():
    with pytest.raises(ValueError):
        PricingTier(Tier.STANDARD, 1.5)  # over 100%
