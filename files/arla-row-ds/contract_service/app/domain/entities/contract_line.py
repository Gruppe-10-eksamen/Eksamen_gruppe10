"""
Entity: ContractLine

En entity har identitet og livscyklus — den spores via et ID og kan ændre sig
over tid uden at holde op med at være "den samme". En ContractLine repræsenterer
ét produkt i en distributøraftale med tilhørende aftalt pris.

Modsætningen til et value object: to ContractLines med samme produktkode men
forskellige ID'er er IKKE den samme linje.
"""
from dataclasses import dataclass


@dataclass
class ContractLine:
    contract_line_id: str   # identitet
    product_code: str       # fx "ARLA-MILK-1L"
    agreed_unit_price: float
    currency: str

    def __post_init__(self):
        if self.agreed_unit_price < 0:
            raise ValueError("agreed_unit_price kan ikke være negativ")
