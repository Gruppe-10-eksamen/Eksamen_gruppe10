"""
Repository: ContractRepository

Repository-mønsteret giver et samlingslignende interface til at hente og gemme
aggregater. Det er ENESTE sted hvor ORM-modeller oversættes til domæneobjekter
og omvendt. Resten af applikationen arbejder kun med domæneobjekter.

_to_domain() er kernen: den rekonstruerer et fuldt DistributorContract-aggregat
(med Distributor, ContractTerms, PricingTier og ContractLines) ud fra de flade
ORM-rækker.
"""
from sqlalchemy.orm import Session

from app.domain.aggregates import DistributorContract
from app.domain.entities import Distributor, ContractLine
from app.domain.value_objects import (
    MarketRegion, Region, PricingTier, Tier, ContractTerms,
)
from app.infrastructure.models import (
    ContractModel, DistributorModel, ContractLineModel,
)


class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_distributor(self, distributor_id: str) -> DistributorContract | None:
        model = (
            self.db.query(ContractModel)
            .filter(ContractModel.distributor_id == distributor_id)
            .first()
        )
        if model is None:
            return None
        return self._to_domain(model)

    def get_by_contract_id(self, contract_id: str) -> DistributorContract | None:
        model = self.db.get(ContractModel, contract_id)
        return self._to_domain(model) if model else None

    def list_all(self) -> list[DistributorContract]:
        return [self._to_domain(m) for m in self.db.query(ContractModel).all()]

    def _to_domain(self, model: ContractModel) -> DistributorContract:
        """Oversæt fra flad ORM-struktur til rigt domæneaggregat."""
        distributor = Distributor(
            distributor_id=model.distributor.distributor_id,
            name=model.distributor.name,
            market_region=MarketRegion(
                region=Region(model.distributor.region),
                currency=model.distributor.currency,
            ),
            is_active=model.distributor.is_active,
        )
        terms = ContractTerms(
            payment_days=model.payment_days,
            minimum_order_quantity=model.minimum_order_quantity,
            valid_from=model.valid_from,
            valid_to=model.valid_to,
        )
        pricing = PricingTier(
            tier=Tier(model.pricing_tier),
            discount_percentage=model.discount_percentage,
        )
        contract = DistributorContract(
            contract_id=model.contract_id,
            distributor=distributor,
            terms=terms,
            pricing_tier=pricing,
        )
        for line in model.lines:
            contract.add_contract_line(
                ContractLine(
                    contract_line_id=line.contract_line_id,
                    product_code=line.product_code,
                    agreed_unit_price=line.agreed_unit_price,
                    currency=line.currency,
                )
            )
        return contract
