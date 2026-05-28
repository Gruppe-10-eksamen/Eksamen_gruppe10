"""
Domain Event: OrderValidated / OrderRejected

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
