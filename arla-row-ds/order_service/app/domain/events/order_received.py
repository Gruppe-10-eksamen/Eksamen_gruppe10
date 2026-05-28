"""
Domain Event: OrderReceived. Udløses når en IncomingOrder registreres
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrderReceived:
    order_id: str
    distributor_id: str
    channel: str
    occurred_at: datetime
