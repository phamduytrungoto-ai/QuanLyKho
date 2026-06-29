"""Material, Category, Unit, Supplier, and MaterialImage models."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Integer, Numeric, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MaterialCategory(Base):
    __tablename__ = "material_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100))
    name_ja: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("material_categories.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent = relationship("MaterialCategory", remote_side="MaterialCategory.id", lazy="selectin")
    materials = relationship("Material", back_populates="category", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Category {self.code}: {self.name}>"


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(50))
    name_ja: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    materials = relationship("Material", back_populates="unit", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Unit {self.code}>"


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(200))
    contact_person: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    tax_code: Mapped[str | None] = mapped_column(String(20))
    lead_time_days: Mapped[int | None] = mapped_column(Integer)
    payment_terms: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    materials = relationship("Material", back_populates="supplier", lazy="selectin")
    receipts = relationship("Receipt", back_populates="supplier", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Supplier {self.code}: {self.name}>"


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    qr_code: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ja: Mapped[str | None] = mapped_column(String(200))
    name_en: Mapped[str | None] = mapped_column(String(200))
    model: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))

    # Foreign keys
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("material_categories.id"))
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"))

    # Type: spare_part, consumable, tool, chemical
    material_type: Mapped[str] = mapped_column(String(20), nullable=False, default="spare_part")

    # Cost & procurement
    price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="VND")
    lifetime_hours: Mapped[int | None] = mapped_column(Integer)
    lead_time_days: Mapped[int | None] = mapped_column(Integer)
    moq: Mapped[int | None] = mapped_column(Integer)  # Minimum Order Quantity

    # Specs
    specifications: Mapped[dict | None] = mapped_column(JSON)
    datasheet_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)

    # Consumption standard (for consumables)
    consumption_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # e.g., 0.15 g/product
    consumption_unit: Mapped[str | None] = mapped_column(String(20))  # e.g., "g/pcs"

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, inactive, discontinued
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("MaterialCategory", back_populates="materials", lazy="selectin")
    unit = relationship("Unit", back_populates="materials", lazy="selectin")
    supplier = relationship("Supplier", back_populates="materials", lazy="selectin")
    images = relationship("MaterialImage", back_populates="material", lazy="selectin", cascade="all, delete-orphan")
    inventory_records = relationship("Inventory", back_populates="material", lazy="selectin")
    min_max_configs = relationship("MaterialMinMax", back_populates="material", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Material {self.code}: {self.name}>"


class MaterialImage(Base):
    __tablename__ = "material_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    material = relationship("Material", back_populates="images", lazy="selectin")

    def __repr__(self) -> str:
        return f"<MaterialImage {self.material_id}: {self.image_url}>"
