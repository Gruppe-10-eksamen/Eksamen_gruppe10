"""
Aggregate Root: DistributorContract

Et aggregat er en konsistensgrænse i domænemodellen — en gruppe objekter der
behandles som én enhed. Aggregate root er den ENESTE indgang til aggregatet:
al adgang til de underliggende entiteter (Distributor, ContractLine) sker
gennem roden. Det sikrer at forretningsreglerne altid håndhæves.

DistributorContract samler:
  - én Distributor (entity)
  - en eller flere ContractLines (entities)
  - ContractTerms (value object)
  - PricingTier (value object)

Eksempel på hvorfor aggregate root er vigtig: man kan ikke tilføje en
ContractLine udenom roden — det sker via add_contract_line(), så vi kan
håndhæve regler (fx ingen dubletter af produktkoder).
"""
from dataclasses import dataclass, field
from datetime import date

from app.domain.entities import Distributor, ContractLine
from app.domain.value_objects import ContractTerms, PricingTier


@dataclass
class DistributorContract:
    contract_id: str            # aggregatets identitet
    distributor: Distributor
    terms: ContractTerms
    pricing_tier: PricingTier
    contract_lines: list[ContractLine] = field(default_factory=list)

    def add_contract_line(self, line: ContractLine) -> None:
        """Forretningsregel: samme produktkode må ikke optræde to gange."""
        if any(cl.product_code == line.product_code for cl in self.contract_lines):
            raise ValueError(
                f"Produktkode {line.product_code} findes allerede i aftalen"
            )
        self.contract_lines.append(line)

    def is_product_allowed(self, product_code: str) -> bool:
        """Bruges af Order Service: må denne distributør bestille dette produkt?"""
        return any(cl.product_code == product_code for cl in self.contract_lines)

    def price_for(self, product_code: str) -> float | None:
        """Returnerer aftalt pris efter rabat, eller None hvis produktet ikke er i aftalen."""
        for cl in self.contract_lines:
            if cl.product_code == product_code:
                discount = self.pricing_tier.discount_percentage
                return round(cl.agreed_unit_price * (1 - discount), 2)
        return None

    def is_valid_on(self, on_date: date) -> bool:
        """Forretningsregel: er aftalen aktiv på ordredatoen?"""
        return self.terms.is_active(on_date) and self.distributor.is_active
