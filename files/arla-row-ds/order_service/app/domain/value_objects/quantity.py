"""
Value Object: Quantity

Den ønskede mængde af en ordrelinje. Indkapsler validering: en mængde kan
ikke være nul eller negativ. Dette er et klassisk eksempel på værdien af
value objects — reglen håndhæves ét sted og kan ikke omgås.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    value: int
    unit: str = "units"

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quantity skal være positiv")
