"""
Value Object: Channel. Den kanal en ordre er modtaget via.
"""
from enum import Enum


class Channel(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    TEAMS = "TEAMS"
    SMS = "SMS"
    API = "API"  # direkte integration (fremtidssikret)
