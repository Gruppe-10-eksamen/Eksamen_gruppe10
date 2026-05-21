"""
Domain Event: OrderValidated / OrderRejected

OrderValidated udløses når en ordre er godkendt og klar til SAP.
OrderRejected udløses når en ordre afvises, med en årsagskode der kan
analyseres i BI-laget (hvilke fejltyper er hyppigst, per distributør/kanal?).
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrderValidated:
    order_id: str
    distributor_id: str
    total_value: float
    occurred_at: datetime


@dataclass(frozen=True)
class OrderRejected:
    order_id: str
    distributor_id: str
    reason: str
    occurred_at: datetime
