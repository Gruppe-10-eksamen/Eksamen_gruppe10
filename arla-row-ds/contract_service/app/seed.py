"""
Seed-script: indsætter testdata (distributøraftaler) til lokal udvikling. Kør: python -m app.seed
"""
import logging
from datetime import date

from app.database import SessionLocal, Base, engine
from app.infrastructure.models import (
    DistributorModel, ContractModel, ContractLineModel,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(ContractModel).count() > 0:
            logger.info("Data findes allerede — springer seeding over.")
            return

        # Distributør 1 — MENA (Puck-marked)
        d1 = DistributorModel(
            distributor_id="DIST-001", name="Gulf Dairy Trading LLC",
            region="MENA", currency="AED", is_active=True,
        )
        c1 = ContractModel(
            contract_id="CON-001", distributor_id="DIST-001",
            payment_days=30, minimum_order_quantity=50,
            valid_from=date(2025, 1, 1), valid_to=date(2026, 12, 31),
            pricing_tier="STRATEGIC", discount_percentage=0.15,
        )
        l1 = ContractLineModel(contract_line_id="CL-001", contract_id="CON-001",
                              product_code="PUCK-CHEESE-200G", agreed_unit_price=12.0, currency="AED")
        l2 = ContractLineModel(contract_line_id="CL-002", contract_id="CON-001",
                              product_code="ARLA-MILK-1L", agreed_unit_price=6.5, currency="AED")

        # Distributør 2 — LATAM
        d2 = DistributorModel(
            distributor_id="DIST-002", name="Distribuidora Láctea SA",
            region="LATAM", currency="USD", is_active=True,
        )
        c2 = ContractModel(
            contract_id="CON-002", distributor_id="DIST-002",
            payment_days=45, minimum_order_quantity=100,
            valid_from=date(2025, 6, 1), valid_to=date(2026, 6, 1),
            pricing_tier="VOLUME", discount_percentage=0.08,
        )
        l3 = ContractLineModel(contract_line_id="CL-003", contract_id="CON-002",
                              product_code="ARLA-BUTTER-250G", agreed_unit_price=3.2, currency="USD")

        db.add_all([d1, d2, c1, c2, l1, l2, l3])
        db.commit()
        logger.info("Seed gennemført: 2 distributører, 2 aftaler, 3 linjer.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
