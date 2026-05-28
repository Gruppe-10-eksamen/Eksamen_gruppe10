"""
Value Object: Quantity. Mængde på en ordrelinje — skal være positiv.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    value: int
    unit: str = "units"

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quantity skal være positiv")
