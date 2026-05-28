"""ACL: ContractClient. Oversætter Contract Service's svar til Order-domænets sprog."""
import logging
import httpx
from app.config import settings

logger = logging.getLogger("order-service.acl")


class ProductCheckResult:
    """Domæne-venligt resultat — ikke Contract Service's rå JSON."""
    def __init__(self, is_allowed: bool, unit_price: float | None,
                 minimum_order_quantity: int, allowed_unit: str = "units"):
        self.is_allowed = is_allowed
        self.unit_price = unit_price
        self.minimum_order_quantity = minimum_order_quantity
        self.allowed_unit = allowed_unit


class ContractClient:
    def __init__(self):
        self.base_url = settings.CONTRACT_SERVICE_URL
        self.headers = {"X-API-Key": settings.CONTRACT_SERVICE_API_KEY}

    def check_product(self, distributor_id: str, product_code: str) -> ProductCheckResult:
        """Spørg Contract Service: må distributøren bestille produktet?"""
        url = f"{self.base_url}/contracts/{distributor_id}/check/{product_code}"
        try:
            resp = httpx.get(url, headers=self.headers, timeout=5.0)
        except httpx.RequestError as exc:
            logger.error("Kunne ikke nå Contract Service: %s", exc)
            raise ContractServiceUnavailable() from exc

        if resp.status_code == 404:
            return ProductCheckResult(False, None, 0)
        resp.raise_for_status()

        data = resp.json()
        return ProductCheckResult(
            is_allowed=data["is_allowed"],
            unit_price=data["unit_price"],
            minimum_order_quantity=data["minimum_order_quantity"],
            allowed_unit=data.get("allowed_unit", "units"),
        )


class ContractServiceUnavailable(Exception):
    """Rejses når Contract Service ikke kan nås."""
    pass