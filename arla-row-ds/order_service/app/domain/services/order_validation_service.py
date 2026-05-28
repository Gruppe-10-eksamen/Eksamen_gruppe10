"""
Domain Service: OrderValidationService.
Validerer en ordre mod distributøraftalen via ContractClient (ACL).
Kalder order.validate() eller order.reject() baseret på valideringsresultatet.
"""
import logging

from app.domain.aggregates import Order
from app.infrastructure.acl import ContractClient, ContractServiceUnavailable

logger = logging.getLogger("order-service.validation")


class OrderValidationService:
    def __init__(self, contract_client: ContractClient):
        self.contract_client = contract_client

    def validate(self, order: Order) -> Order:
        """
        Validér ordren mod distributøraftalen. Reglerne:
          1. Hver ordrelinjes produkt skal være tilladt i aftalen
          2. Den samlede mængde skal opfylde minimumsmængden
        Ved succes: order.validate(priser). Ved fejl: order.reject(årsag).
        """
        priced_lines: dict[str, float] = {}
        min_quantity = 0

        for line in order.lines:
            try:
                check = self.contract_client.check_product(
                    order.distributor_id, line.product_code
                )
            except ContractServiceUnavailable:
                # Fejlhåndtering: kan vi ikke validere, afviser vi ikke —
                # vi lader fejlen boble op så API'et kan returnere 503.
                logger.error("Validering afbrudt: Contract Service utilgængelig")
                raise

            if not check.is_allowed:
                reason = f"Produkt {line.product_code} er ikke tilladt i aftalen"
                logger.info("Ordre %s afvist: %s", order.order_id, reason)
                order.reject(reason)
                return order

            priced_lines[line.product_code] = check.unit_price
            min_quantity = max(min_quantity, check.minimum_order_quantity)

        # Regel 2: minimumsmængde
        if order.total_quantity < min_quantity:
            reason = (
                f"Samlet mængde {order.total_quantity} er under "
                f"minimumskravet på {min_quantity}"
            )
            logger.info("Ordre %s afvist: %s", order.order_id, reason)
            order.reject(reason)
            return order

        order.validate(priced_lines)
        logger.info("Ordre %s valideret. Værdi: %.2f", order.order_id, order.total_value)
        return order
