"""
Entity: Distributor

En ekstern handelspartner der køber og videredistribuerer Arlas produkter på
et givent marked. Distributoren har identitet (distributor_id) og spores
over tid — kontaktoplysninger kan ændre sig, men det er stadig samme distributør.
"""
from dataclasses import dataclass

from app.domain.value_objects import MarketRegion


@dataclass
class Distributor:
    distributor_id: str    # identitet
    name: str
    market_region: MarketRegion
    is_active: bool = True
