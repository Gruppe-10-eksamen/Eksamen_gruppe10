"""
Value Object: OrderStatus Ordrens tilstand i livscyklussen. 
"""
from enum import Enum


class OrderStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    FORWARDED_TO_SAP = "FORWARDED_TO_SAP"
