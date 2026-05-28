"""Entity: ContractLine. Ét produkt i en distributøraftale med aftalt pris. Identitet via contract_line_id."""
from dataclasses import dataclass


@dataclass
class ContractLine:
    contract_line_id: str
    product_code: str
    agreed_unit_price: float
    currency: str
    allowed_unit: Mapped[str] = mapped_column(String, nullable=False, default="units")

    def __post_init__(self):
        if self.agreed_unit_price < 0:
            raise ValueError("agreed_unit_price kan ikke være negativ")