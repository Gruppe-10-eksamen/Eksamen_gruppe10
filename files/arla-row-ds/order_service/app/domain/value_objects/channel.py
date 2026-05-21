"""
Value Object: Channel

Den kanal en ordre er modtaget via. I AS-IS-analysen er det netop spredningen
af kanaler (email, WhatsApp, Teams, Excel) der skaber kompleksitet. Ved at
modellere kanalen eksplicit kan vi spore hvor ordrer kommer fra og analysere
fejlrater per kanal i BI-laget.
"""
from enum import Enum


class Channel(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    TEAMS = "TEAMS"
    EXCEL = "EXCEL"
    API = "API"  # direkte integration (fremtidssikret)
