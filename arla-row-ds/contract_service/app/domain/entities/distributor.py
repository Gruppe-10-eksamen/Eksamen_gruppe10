"""
Entity: Distributor. Ekstern handelspartner med unik identitet (distributor_id).
"""
from dataclasses import dataclass

from app.domain.value_objects import MarketRegion


@dataclass
class Distributor:
    distributor_id: str    # identitet
    name: str
    market_region: MarketRegion
    is_active: bool = True
