"""Warehouse and Location models."""

from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    # Types: main, chemical, spare_part, inspection, defective, return_supplier
    warehouse_type: Mapped[str] = mapped_column(String(30), default="main")
    address: Mapped[str | None] = mapped_column(String(200))
    manager: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    locations = relationship("Location", back_populates="warehouse", lazy="selectin", cascade="all, delete-orphan")
    min_max_configs = relationship("MaterialMinMax", back_populates="warehouse", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Warehouse {self.code}: {self.name}>"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    rack: Mapped[str | None] = mapped_column(String(10))   # Kệ A, B, C...
    level: Mapped[str | None] = mapped_column(String(10))   # Tầng 1, 2, 3...
    bin: Mapped[str | None] = mapped_column(String(10))     # Ô 01, 02, 03...
    full_path: Mapped[str | None] = mapped_column(String(100))  # e.g., "Kho chính > Kệ A > Tầng 2 > Ô 05"
    description: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    warehouse = relationship("Warehouse", back_populates="locations", lazy="selectin")
    inventory_records = relationship("Inventory", back_populates="location", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Location {self.code}: {self.full_path}>"
