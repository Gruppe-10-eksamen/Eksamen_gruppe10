"""
Entity: ContractLine. Ét produkt i en distributøraftale med aftalt pris. Identitet via contract_line_id.
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
