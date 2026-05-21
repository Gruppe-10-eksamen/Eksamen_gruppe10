"""
Value Object: OrderStatus

Ordrens tilstand i livscyklussen. Bemærk distinktionen fra rapporten:
RECEIVED = en IncomingOrder (endnu ikke valideret)
VALIDATED = en gyldig Order klar til SAP
REJECTED = afvist med årsag

Som value object er status uforanderlig — en statusovergang skaber en ny
værdi frem for at mutere den eksisterende.
"""
from enum import Enum


class OrderStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    FORWARDED_TO_SAP = "FORWARDED_TO_SAP"
