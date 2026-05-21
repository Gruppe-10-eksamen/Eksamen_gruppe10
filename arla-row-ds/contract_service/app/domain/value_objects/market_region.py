"""
Value Object: MarketRegion

Et value object er identitetsløst og uforanderligt (immutable). Det beskriver
en egenskab, ikke en ting med livscyklus. MarketRegion repræsenterer den
geografiske og regulatoriske markedskategori en distributør opererer i.

Vi bruger `frozen=True` for at gøre objektet uforanderligt — to MarketRegion
med samme værdi er per definition ens (value equality, ikke identity equality).
"""
from dataclasses import dataclass
from enum import Enum


class Region(str, Enum):
    LATAM = "LATAM"          # Latinamerika
    AFRICA = "AFRICA"        # Afrika
    MENA = "MENA"            # Mellemøsten og Nordafrika
    EUROPE_OTHER = "EUROPE_OTHER"  # Udvalgte europæiske markeder uden for kernemarkederne


@dataclass(frozen=True)
class MarketRegion:
    region: Region
    currency: str  # fx "USD", "EUR", "AED"

    def __post_init__(self):
        if len(self.currency) != 3:
            raise ValueError("Currency skal være en 3-bogstavs ISO-kode, fx 'USD'")
