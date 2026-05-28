"""
Pydantic-schemas definerer API'ets ud-/indgående kontrakt. De er adskilt fra
domæneobjekterne, så API-formatet kan ændre sig uafhængigt af domænemodellen.
"""
from pydantic import BaseModel


class ContractLineOut(BaseModel):
    product_code: str
    agreed_unit_price: float
    currency: str
    allowed_unit: str = "units"


class ContractOut(BaseModel):
    contract_id: str
    distributor_id: str
    distributor_name: str
    region: str
    currency: str
    is_active: bool
    minimum_order_quantity: int
    discount_percentage: float
    lines: list[ContractLineOut]


class ValidationCheckOut(BaseModel):
    """Svar på Order Service's valideringsforespørgsel."""
    distributor_id: str
    product_code: str
    is_allowed: bool
    unit_price: float | None
    minimum_order_quantity: int
    allowed_unit: str = "units"
