"""
Order Service endpoints — det centrale ordreflow.

POST /orders     -> modtag en IncomingOrder, validér mod aftalen, persistér,
                    og send til SAP hvis valideret. Dette er hele end-to-end
                    flowet: Distributør -> Order Service -> (ACL) Contract
                    Service -> PostgreSQL -> SAP.
GET  /orders     -> liste over alle ordrer (bruges bl.a. af Power BI)
GET  /orders/{id}-> enkelt ordre
"""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_api_key
from app.domain.aggregates import Order, OrderLine
from app.domain.value_objects import Channel, Quantity, OrderStatus
from app.domain.services.order_validation_service import OrderValidationService
from app.infrastructure.repositories import OrderRepository
from app.infrastructure.acl import ContractClient, ContractServiceUnavailable
from app.infrastructure.sap import SapAdapter
from app.api.schemas import OrderIn, OrderOut, OrderLineOut

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger("order-service.api")


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderIn, db: Session = Depends(get_db), _=Depends(require_api_key)):
    # 1. Byg Order-aggregatet ud fra den indkomne ordre (IncomingOrder)
    try:
        channel = Channel(payload.channel.upper())
    except ValueError:
        raise HTTPException(422, f"Ukendt kanal: {payload.channel}")

    order = Order(
        order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
        distributor_id=payload.distributor_id,
        channel=channel,
        order_date=payload.order_date,
    )
    for line in payload.lines:
        order.add_line(OrderLine(
            order_line_id=f"OL-{uuid.uuid4().hex[:6].upper()}",
            product_code=line.product_code,
            quantity=Quantity(line.quantity, line.unit),
        ))
    order.register_received()

    # 2. Validér mod distributøraftalen via domain service (bruger ACL)
    validation_service = OrderValidationService(ContractClient())
    try:
        order = validation_service.validate(order)
    except ContractServiceUnavailable:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Contract Service er utilgængelig — ordren kunne ikke valideres",
        )

    # 3. Persistér ordren (valideret eller afvist)
    repo = OrderRepository(db)
    repo.save(order)

    # 4. Hvis valideret -> send til SAP via adapter, og markér
    sap_order_id = None
    if order.status == OrderStatus.VALIDATED:
        sap_order_id = SapAdapter().forward_order(order)
        order.mark_forwarded_to_sap()
        repo.save(order)

    # 5. Log de domain events der blev udløst undervejs
    for event in order.pull_events():
        logger.info("Event: %s", type(event).__name__)

    return _to_out(order, sap_order_id)


@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), _=Depends(require_api_key)):
    repo = OrderRepository(db)
    return [_to_out(o) for o in repo.list_all()]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db), _=Depends(require_api_key)):
    repo = OrderRepository(db)
    order = repo.get(order_id)
    if order is None:
        raise HTTPException(404, f"Ordre {order_id} ikke fundet")
    return _to_out(order)


def _to_out(order: Order, sap_order_id: str | None = None) -> OrderOut:
    return OrderOut(
        order_id=order.order_id,
        distributor_id=order.distributor_id,
        channel=order.channel.value,
        order_date=order.order_date,
        status=order.status.value,
        rejection_reason=order.rejection_reason,
        total_value=order.total_value,
        total_quantity=order.total_quantity,
        sap_order_id=sap_order_id,
        lines=[
            OrderLineOut(
                product_code=l.product_code,
                quantity=l.quantity.value,
                unit_price=l.unit_price,
                line_total=l.line_total,
            )
            for l in order.lines
        ],
    )
