"""
Contract Service endpoints.

GET /contracts                      -> liste over alle aftaler
GET /contracts/{distributor_id}     -> aftale for en distributør
GET /contracts/{distributor_id}/check/{product_code}
    -> bruges af Order Service via Anti-Corruption Layer til at validere en
       ordrelinje: må distributøren bestille produktet, til hvilken pris,
       og hvad er minimumsmængden?
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_api_key
from app.infrastructure.repositories import ContractRepository
from app.api.schemas import ContractOut, ContractLineOut, ValidationCheckOut

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=list[ContractOut])
def list_contracts(db: Session = Depends(get_db), _=Depends(require_api_key)):
    repo = ContractRepository(db)
    return [_to_out(c) for c in repo.list_all()]


@router.get("/{distributor_id}", response_model=ContractOut)
def get_contract(distributor_id: str, db: Session = Depends(get_db), _=Depends(require_api_key)):
    repo = ContractRepository(db)
    contract = repo.get_by_distributor(distributor_id)
    if contract is None:
        raise HTTPException(404, f"Ingen aftale fundet for distributør {distributor_id}")
    return _to_out(contract)


@router.get("/{distributor_id}/check/{product_code}", response_model=ValidationCheckOut)
def check_product(distributor_id: str, product_code: str,
                  db: Session = Depends(get_db), _=Depends(require_api_key)):
    repo = ContractRepository(db)
    contract = repo.get_by_distributor(distributor_id)
    if contract is None:
        raise HTTPException(404, f"Ingen aftale fundet for distributør {distributor_id}")

    allowed = contract.is_product_allowed(product_code) and contract.is_valid_on(date.today())
    return ValidationCheckOut(
        distributor_id=distributor_id,
        product_code=product_code,
        is_allowed=allowed,
        unit_price=contract.price_for(product_code) if allowed else None,
        minimum_order_quantity=contract.terms.minimum_order_quantity,
        allowed_unit=contract.allowed_unit_for(product_code) if allowed else "units",
    )


def _to_out(contract) -> ContractOut:
    return ContractOut(
        contract_id=contract.contract_id,
        distributor_id=contract.distributor.distributor_id,
        distributor_name=contract.distributor.name,
        region=contract.distributor.market_region.region.value,
        currency=contract.distributor.market_region.currency,
        is_active=contract.distributor.is_active,
        minimum_order_quantity=contract.terms.minimum_order_quantity,
        discount_percentage=contract.pricing_tier.discount_percentage,
        lines=[
            ContractLineOut(
                product_code=cl.product_code,
                agreed_unit_price=cl.agreed_unit_price,
                currency=cl.currency,
                allowed_unit=cl.allowed_unit
            )
            for cl in contract.contract_lines
        ],
    )
