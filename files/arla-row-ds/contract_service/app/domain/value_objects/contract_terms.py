"""
Value Object: ContractTerms

De overordnede vilkår i en distributøraftale: betalingsbetingelser,
minimumsmængder og gyldighedsperiode. Disse vilkår bruges af Order Service
til at validere om en ordre er i overensstemmelse med aftalen.
"""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ContractTerms:
    payment_days: int          # fx 30 for "netto 30 dage"
    minimum_order_quantity: int  # mindste tilladte ordremængde
    valid_from: date
    valid_to: date

    def __post_init__(self):
        if self.valid_to <= self.valid_from:
            raise ValueError("valid_to skal være efter valid_from")
        if self.minimum_order_quantity < 0:
            raise ValueError("minimum_order_quantity kan ikke være negativ")

    def is_active(self, on_date: date) -> bool:
        """Forretningsregel: er aftalen gyldig på en given dato?"""
        return self.valid_from <= on_date <= self.valid_to
