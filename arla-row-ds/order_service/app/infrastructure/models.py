"""
ORM-modeller for Order Service. Afspejler domænemodellen:
  orders        <- Order (aggregate root)
  order_lines   <- OrderLine (entity)
Value objects (status, channel) lagres som kolonner.
"""
from datetime import date

from sqlalchemy import String, Float, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class OrderModel(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    distributor_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String, nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    total_value: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lines: Mapped[list["OrderLineModel"]] = relationship(
        cascade="all, delete-orphan"
    )


class OrderLineModel(Base):
    __tablename__ = "order_lines"

    order_line_id: Mapped[str] = mapped_column(String, primary_key=True)
    order_id: Mapped[str] = mapped_column(
        String, ForeignKey("orders.order_id"), nullable=False
    )
    product_code: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String, default="units")
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
