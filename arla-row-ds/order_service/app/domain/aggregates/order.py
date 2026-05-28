"""
Aggregate Root: Order.
Håndhæver ordrens livscyklus: RECEIVED → VALIDATED/REJECTED → FORWARDED_TO_SAP.
"""
from dataclasses import dataclass, field
from datetime import datetime, date

from app.domain.value_objects import Channel, OrderStatus, Quantity
from app.domain.events import OrderReceived, OrderValidated, OrderRejected


@dataclass
class OrderLine:
    """Entity: en produktlinje i ordren. Har identitet via order_line_id."""
    order_line_id: str
    product_code: str
    quantity: Quantity
    unit_price: float | None = None  # sættes ved validering ud fra kontrakten

    @property
    def line_total(self) -> float:
        if self.unit_price is None:
            return 0.0
        return round(self.unit_price * self.quantity.value, 2)


@dataclass
class Order:
    order_id: str                 # aggregatets identitet
    distributor_id: str
    channel: Channel
    order_date: date
    status: OrderStatus = OrderStatus.RECEIVED
    rejection_reason: str | None = None
    lines: list[OrderLine] = field(default_factory=list)
    _events: list = field(default_factory=list, repr=False)

    # --- Opbygning ---
    def add_line(self, line: OrderLine) -> None:
        if self.status != OrderStatus.RECEIVED:
            raise ValueError("Kan ikke tilføje linjer til en allerede behandlet ordre")
        self.lines.append(line)

    def register_received(self) -> None:
        """Udløser OrderReceived-event."""
        self._events.append(OrderReceived(
            order_id=self.order_id, distributor_id=self.distributor_id,
            channel=self.channel.value, occurred_at=datetime.utcnow(),
        ))

    # --- Livscyklus-overgange (håndhæver regler) ---
    def validate(self, priced_lines: dict[str, float]) -> None:
        """
        Markér ordren som valideret. priced_lines mapper product_code -> unit_price
        (kommer fra Contract Service via ACL). Sætter priser på linjerne og
        skifter status til VALIDATED.
        """
        if self.status != OrderStatus.RECEIVED:
            raise ValueError("Kun en RECEIVED-ordre kan valideres")
        for line in self.lines:
            line.unit_price = priced_lines[line.product_code]
        self.status = OrderStatus.VALIDATED
        self._events.append(OrderValidated(
            order_id=self.order_id, distributor_id=self.distributor_id,
            total_value=self.total_value, occurred_at=datetime.utcnow(),
        ))

    def reject(self, reason: str) -> None:
        if self.status != OrderStatus.RECEIVED:
            raise ValueError("Kun en RECEIVED-ordre kan afvises")
        self.status = OrderStatus.REJECTED
        self.rejection_reason = reason
        self._events.append(OrderRejected(
            order_id=self.order_id, distributor_id=self.distributor_id,
            reason=reason, occurred_at=datetime.utcnow(),
        ))

    def mark_forwarded_to_sap(self) -> None:
        if self.status != OrderStatus.VALIDATED:
            raise ValueError("Kun en VALIDATED-ordre kan sendes til SAP")
        self.status = OrderStatus.FORWARDED_TO_SAP

    # --- Beregninger ---
    @property
    def total_value(self) -> float:
        return round(sum(line.line_total for line in self.lines), 2)

    @property
    def total_quantity(self) -> int:
        return sum(line.quantity.value for line in self.lines)

    def pull_events(self) -> list:
        """Hent og ryd de akkumulerede events (til publicering)."""
        events, self._events = self._events, []
        return events
