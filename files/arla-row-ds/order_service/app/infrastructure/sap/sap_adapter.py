"""
SAP-adapter (MOCK)

Dette er integrationsleddet til Arlas SAP-system. Det ligger bevidst i
infrastrukturlaget — domænet kender ikke til SAP. Adapteren oversætter en
valideret Order til det format SAP forventer.

I denne MVP er SAP-kaldet mocket: i stedet for at kalde et rigtigt SAP-endpoint
logger vi payloaden og returnerer et fiktivt SAP-ordrenummer. Når I får adgang
til et rigtigt SAP-endpoint, erstatter I blot indholdet af forward_order() —
resten af systemet skal ikke ændres. Det er hele pointen med adapter-mønsteret.
"""
import logging
import uuid

logger = logging.getLogger("order-service.sap")


class SapAdapter:
    def forward_order(self, order) -> str:
        """
        'Send' den validerede ordre til SAP. Returnerer et SAP-ordrenummer.

        I produktion ville her stå noget i retning af:
            resp = httpx.post(SAP_URL, json=payload, headers=...)
            return resp.json()["sap_order_id"]
        """
        payload = self._to_sap_payload(order)
        logger.info("[MOCK SAP] Modtager ordre %s: %s", order.order_id, payload)
        sap_order_id = f"SAP-{uuid.uuid4().hex[:8].upper()}"
        logger.info("[MOCK SAP] Oprettet med SAP-ordrenummer %s", sap_order_id)
        return sap_order_id

    def _to_sap_payload(self, order) -> dict:
        """Oversæt domænemodel -> SAP-format (SAP bruger andre feltnavne)."""
        return {
            "SalesOrder": {
                "SoldToParty": order.distributor_id,
                "RequestedDeliveryDate": order.order_date.isoformat(),
                "Items": [
                    {
                        "Material": line.product_code,
                        "RequestedQuantity": line.quantity.value,
                        "NetPrice": line.unit_price,
                    }
                    for line in order.lines
                ],
            }
        }
