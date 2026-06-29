"""Issue (Phiếu xuất kho) models."""

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    issue_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Types: repair, production, testing, scrap, transfer
    issue_type: Mapped[str] = mapped_column(String(20), nullable=False, default="production")

    # Context
    machine: Mapped[str | None] = mapped_column(String(50))
    line: Mapped[str | None] = mapped_column(String(30))
    shift: Mapped[str | None] = mapped_column(String(10))  # Ca: A, B, C
    receiver: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(Text)
    work_order: Mapped[str | None] = mapped_column(String(30))
    remark: Mapped[str | None] = mapped_column(Text)

    # Status: draft, pending_approval, approved, cancelled
    status: Mapped[str] = mapped_column(String(20), default="draft")
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")
    approver = relationship("User", foreign_keys=[approved_by], lazy="selectin")
    items = relationship("IssueItem", back_populates="issue", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Issue {self.issue_number} ({self.status})>"


class IssueItem(Base):
    __tablename__ = "issue_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    lot_number: Mapped[str | None] = mapped_column(String(50))
    serial_number: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)

    # Relationships
    issue = relationship("Issue", back_populates="items", lazy="selectin")
    material = relationship("Material", lazy="selectin")
    location = relationship("Location", lazy="selectin")

    def __repr__(self) -> str:
        return f"<IssueItem issue={self.issue_id} material={self.material_id} qty={self.quantity}>"
