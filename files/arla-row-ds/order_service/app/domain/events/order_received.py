"""
Domain Event: OrderReceived

Domain events repræsenterer noget vigtigt der ER SKET i domænet (datid).
OrderReceived udløses når en IncomingOrder registreres. Events muliggør løs
kobling: andre dele af systemet kan reagere uden at ordrelogikken kender til dem.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrderReceived:
    order_id: str
    distributor_id: str
    channel: str
    occurred_at: datetime
