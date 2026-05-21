"""
SQLAlchemy ORM-modeller. Dette er PERSISTERINGSLAGET — det er bevidst adskilt
fra domænemodellen. Domæneobjekterne (DistributorContract osv.) kender ikke til
databasen; repository'et oversætter mellem de to.

Læg mærke til hvordan tabelstrukturen direkte afspejler domænemodellen:
  - contracts            <- DistributorContract (aggregate root)
  - distributors         <- Distributor (entity)
  - contract_lines       <- ContractLine (entity)
Value objects (terms, pricing) lagres som kolonner direkte på contracts.
"""
from sqlalchemy import String, Float, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DistributorModel(Base):
    __tablename__ = "distributors"

    distributor_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ContractModel(Base):
    __tablename__ = "contracts"

    contract_id: Mapped[str] = mapped_column(String, primary_key=True)
    distributor_id: Mapped[str] = mapped_column(
        String, ForeignKey("distributors.distributor_id"), nullable=False
    )
    # ContractTerms (value object) flades ud som kolonner
    payment_days: Mapped[int] = mapped_column(Integer, nullable=False)
    minimum_order_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_from: Mapped[Date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[Date] = mapped_column(Date, nullable=False)
    # PricingTier (value object) flades ud som kolonner
    pricing_tier: Mapped[str] = mapped_column(String, nullable=False)
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=False)

    distributor: Mapped["DistributorModel"] = relationship()
    lines: Mapped[list["ContractLineModel"]] = relationship(
        cascade="all, delete-orphan"
    )


class ContractLineModel(Base):
    __tablename__ = "contract_lines"

    contract_line_id: Mapped[str] = mapped_column(String, primary_key=True)
    contract_id: Mapped[str] = mapped_column(
        String, ForeignKey("contracts.contract_id"), nullable=False
    )
    product_code: Mapped[str] = mapped_column(String, nullable=False)
    agreed_unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
