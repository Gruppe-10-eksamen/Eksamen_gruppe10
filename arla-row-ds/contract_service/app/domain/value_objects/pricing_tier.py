"""
Value Object: PricingTier. Aftalt prisniveau og rabat for en distributør.
"""
from dataclasses import dataclass
from enum import Enum


class Tier(str, Enum):
    STANDARD = "STANDARD"
    VOLUME = "VOLUME"        # Rabat ved høj volumen
    STRATEGIC = "STRATEGIC"  # Strategisk partner med særlige vilkår


@dataclass(frozen=True)
class PricingTier:
    tier: Tier
    discount_percentage: float  # fx 0.10 for 10% rabat

    def __post_init__(self):
        if not 0 <= self.discount_percentage <= 1:
            raise ValueError("discount_percentage skal være mellem 0 og 1")
