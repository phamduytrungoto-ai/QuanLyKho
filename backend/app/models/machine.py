"""Machine, Production Line, Parts Tracking, and Maintenance models (Phase 2)."""

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Text, Integer, Numeric, Boolean, Date, DateTime, ForeignKey, JSON, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductionLine(Base):
    __tablename__ = "production_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100))
    area: Mapped[str | None] = mapped_column(String(50))  # e.g., "SMT", "Assembly", "Testing"
    description: Mapped[str | None] = mapped_column(Text)
    manager: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    machines = relationship("Machine", back_populates="line", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ProductionLine {self.code}: {self.name}>"


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(200))
    # Types: smt, assembly, testing, packaging, injection, cnc, press, welding, other
    machine_type: Mapped[str] = mapped_column(String(30), nullable=False, default="other")
    model: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    serial_number: Mapped[str | None] = mapped_column(String(100))

    # Location
    line_id: Mapped[int | None] = mapped_column(ForeignKey("production_lines.id"), index=True)
    location: Mapped[str | None] = mapped_column(String(100))  # Physical position description

    # Dates & Status
    install_date: Mapped[date | None] = mapped_column(Date)
    warranty_expiry: Mapped[date | None] = mapped_column(Date)
    # Status: running, idle, broken, maintenance, decommissioned
    status: Mapped[str] = mapped_column(String(20), default="idle")

    # Running hours tracking
    current_running_hours: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Maintenance info
    last_maintenance_date: Mapped[date | None] = mapped_column(Date)
    next_maintenance_date: Mapped[date | None] = mapped_column(Date)
    maintenance_interval_hours: Mapped[int | None] = mapped_column(Integer)  # PM every X hours

    # Technical specs
    specifications: Mapped[dict | None] = mapped_column(JSON)
    image_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    line = relationship("ProductionLine", back_populates="machines", lazy="selectin")
    parts = relationship("MachinePart", back_populates="machine", lazy="selectin", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="machine", lazy="selectin",
                                     order_by="MaintenanceLog.maintenance_date.desc()")
    running_hours = relationship("MachineRunningHour", back_populates="machine", lazy="selectin",
                                  order_by="MachineRunningHour.record_date.desc()")

    def __repr__(self) -> str:
        return f"<Machine {self.code}: {self.name} ({self.status})>"


class MachinePart(Base):
    """Tracks which materials/parts are currently installed on a machine."""
    __tablename__ = "machine_parts"
    __table_args__ = (
        UniqueConstraint("machine_id", "material_id", "position", name="uq_machine_part_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False, index=True)

    position: Mapped[str | None] = mapped_column(String(100))  # e.g., "Head Unit #1", "Conveyor Belt"

    # Lifetime tracking
    lifetime_hours: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # Total expected lifetime in hours
    current_hours: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Hours used since install
    lifetime_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=100)  # % remaining

    # Dates
    installed_date: Mapped[date | None] = mapped_column(Date)
    expected_replace_date: Mapped[date | None] = mapped_column(Date)
    last_replaced_date: Mapped[date | None] = mapped_column(Date)

    # Status: active, warning (<30%), critical (<10%), expired (0%), replaced
    status: Mapped[str] = mapped_column(String(20), default="active")

    serial_number: Mapped[str | None] = mapped_column(String(100))
    lot_number: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    machine = relationship("Machine", back_populates="parts", lazy="selectin")
    material = relationship("Material", lazy="selectin")

    def __repr__(self) -> str:
        return f"<MachinePart machine={self.machine_id} material={self.material_id} life={self.lifetime_percentage}%>"


class MaintenanceLog(Base):
    """Maintenance/repair log entry for a machine."""
    __tablename__ = "maintenance_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    log_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)

    # Types: corrective (sửa hỏng), preventive (bảo trì định kỳ), predictive (dự đoán), emergency (khẩn cấp)
    maintenance_type: Mapped[str] = mapped_column(String(20), nullable=False, default="corrective")
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False)
    shift: Mapped[str | None] = mapped_column(String(10))  # Ca: A, B, C

    # Machine running hours at the time of maintenance
    running_hours_at_time: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text)
    action_taken: Mapped[str | None] = mapped_column(Text)
    downtime_hours: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))  # How long machine was down

    # Link to issue (if parts were issued from warehouse)
    issue_id: Mapped[int | None] = mapped_column(ForeignKey("issues.id"))

    # Who performed
    performed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Status: open, in_progress, completed, cancelled
    status: Mapped[str] = mapped_column(String(20), default="completed")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_logs", lazy="selectin")
    performer = relationship("User", lazy="selectin")
    issue = relationship("Issue", lazy="selectin")
    items = relationship("MaintenanceLogItem", back_populates="log", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<MaintenanceLog {self.log_number} machine={self.machine_id} ({self.maintenance_type})>"


class MaintenanceLogItem(Base):
    """Parts/materials used during a maintenance event."""
    __tablename__ = "maintenance_log_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    log_id: Mapped[int] = mapped_column(ForeignKey("maintenance_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False)

    # Which old part was replaced (if applicable)
    old_part_id: Mapped[int | None] = mapped_column(ForeignKey("machine_parts.id"))

    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=1, nullable=False)
    # Action types: replaced, consumed, inspected
    action_type: Mapped[str] = mapped_column(String(20), default="replaced")
    note: Mapped[str | None] = mapped_column(Text)

    # Relationships
    log = relationship("MaintenanceLog", back_populates="items", lazy="selectin")
    material = relationship("Material", lazy="selectin")
    old_part = relationship("MachinePart", lazy="selectin")

    def __repr__(self) -> str:
        return f"<MaintenanceLogItem log={self.log_id} material={self.material_id}>"


class MachineRunningHour(Base):
    """Daily running hours record for a machine."""
    __tablename__ = "machine_running_hours"
    __table_args__ = (
        UniqueConstraint("machine_id", "record_date", "shift", name="uq_running_hours_machine_date_shift"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    running_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    cumulative_hours: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    shift: Mapped[str | None] = mapped_column(String(10))  # Ca A, B, C or null for total
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    machine = relationship("Machine", back_populates="running_hours", lazy="selectin")
    recorder = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<RunningHour machine={self.machine_id} date={self.record_date} hours={self.running_hours}>"
