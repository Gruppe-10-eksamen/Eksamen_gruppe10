"""
Value Object: MarketRegion. Geografisk og regulatorisk markedskategori for en distributør.
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
