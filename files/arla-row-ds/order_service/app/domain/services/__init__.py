"""
Domain services.

Bemærk: vi importerer IKKE services eagerly her, fordi OrderValidationService
afhænger af infrastruktur (httpx via ACL), mens DemandForecastService kun
afhænger af numpy/sklearn. Eager import ville unødigt koble de to. Importér
i stedet den konkrete service direkte hvor den bruges:

    from app.domain.services.order_validation_service import OrderValidationService
    from app.domain.services.demand_forecast_service import DemandForecastService
"""
