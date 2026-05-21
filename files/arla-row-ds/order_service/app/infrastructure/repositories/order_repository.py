"""
Repository: OrderRepository

Oversætter mellem Order-aggregatet og ORM-modellerne, og persisterer ordrer
til PostgreSQL. Som i Contract Service er dette eneste sted hvor domæne <-> ORM
oversættelsen sker.
"""
from sqlalchemy.orm import Session

from app.domain.aggregates import Order, OrderLine
from app.domain.value_objects import Channel, OrderStatus, Quantity
from app.infrastructure.models import OrderModel, OrderLineModel


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, order: Order) -> None:
        """Gem eller opdater en ordre (upsert)."""
        model = self.db.get(OrderModel, order.order_id)
        if model is None:
            model = OrderModel(order_id=order.order_id)
            self.db.add(model)

        model.distributor_id = order.distributor_id
        model.channel = order.channel.value
        model.order_date = order.order_date
        model.status = order.status.value
        model.rejection_reason = order.rejection_reason
        model.total_value = order.total_value

        # Genopbyg linjer
        model.lines.clear()
        for line in order.lines:
            model.lines.append(OrderLineModel(
                order_line_id=line.order_line_id,
                order_id=order.order_id,
                product_code=line.product_code,
                quantity=line.quantity.value,
                unit=line.quantity.unit,
                unit_price=line.unit_price,
            ))
        self.db.commit()

    def get(self, order_id: str) -> Order | None:
        model = self.db.get(OrderModel, order_id)
        return self._to_domain(model) if model else None

    def list_all(self) -> list[Order]:
        return [self._to_domain(m) for m in self.db.query(OrderModel).all()]

    def list_validated(self) -> list[Order]:
        models = (
            self.db.query(OrderModel)
            .filter(OrderModel.status.in_(["VALIDATED", "FORWARDED_TO_SAP"]))
            .all()
        )
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: OrderModel) -> Order:
        order = Order(
            order_id=model.order_id,
            distributor_id=model.distributor_id,
            channel=Channel(model.channel),
            order_date=model.order_date,
            status=OrderStatus(model.status),
            rejection_reason=model.rejection_reason,
        )
        for lm in model.lines:
            order.lines.append(OrderLine(
                order_line_id=lm.order_line_id,
                product_code=lm.product_code,
                quantity=Quantity(lm.quantity, lm.unit),
                unit_price=lm.unit_price,
            ))
        return order
