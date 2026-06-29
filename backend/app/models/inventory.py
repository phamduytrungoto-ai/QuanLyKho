"""Inventory, InventoryTransaction, and MaterialMinMax models."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("material_id", "location_id", name="uq_inventory_material_location"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    reserved_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    material = relationship("Material", back_populates="inventory_records", lazy="selectin")
    location = relationship("Location", back_populates="inventory_records", lazy="selectin")
    transactions = relationship("InventoryTransaction", back_populates="inventory", lazy="selectin",
                                order_by="InventoryTransaction.created_at.desc()")

    @property
    def available_quantity(self) -> Decimal:
        return self.quantity - self.reserved_quantity

    def __repr__(self) -> str:
        return f"<Inventory material={self.material_id} loc={self.location_id} qty={self.quantity}>"


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"), nullable=False, index=True)
    # Types: receipt_in, issue_out, adjustment, transfer_in, transfer_out, return_in, scrap
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(20))  # receipt, issue, adjustment
    reference_id: Mapped[int | None] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    inventory = relationship("Inventory", back_populates="transactions", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_type} qty={self.quantity}>"


class MaterialMinMax(Base):
    __tablename__ = "material_min_max"
    __table_args__ = (
        UniqueConstraint("material_id", "warehouse_id", name="uq_minmax_material_warehouse"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False, index=True)
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id"), index=True)
    min_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    max_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    reorder_point: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    reorder_quantity: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    avg_daily_usage: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    material = relationship("Material", back_populates="min_max_configs", lazy="selectin")
    warehouse = relationship("Warehouse", back_populates="min_max_configs", lazy="selectin")

    def __repr__(self) -> str:
        return f"<MinMax material={self.material_id} min={self.min_quantity} max={self.max_quantity}>"
