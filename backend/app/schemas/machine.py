"""Machine, Production Line, Parts Tracking, and Maintenance schemas (Phase 2)."""

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# ============== Production Line ==============
class LineBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    name_en: str | None = None
    area: str | None = None
    description: str | None = None
    manager: str | None = None


class LineCreate(LineBase):
    pass


class LineUpdate(BaseModel):
    name: str | None = None
    name_en: str | None = None
    area: str | None = None
    description: str | None = None
    manager: str | None = None
    is_active: bool | None = None


class LineResponse(LineBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============== Machine ==============
class MachineBase(BaseModel):
    code: str = Field(..., max_length=30)
    name: str = Field(..., max_length=200)
    name_en: str | None = None
    machine_type: str = "other"
    model: str | None = None
    manufacturer: str | None = None
    serial_number: str | None = None
    line_id: int | None = None
    location: str | None = None
    install_date: date | None = None
    warranty_expiry: date | None = None
    status: str = "idle"
    maintenance_interval_hours: int | None = None
    specifications: dict | None = None
    image_url: str | None = None
    description: str | None = None


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    name: str | None = None
    name_en: str | None = None
    machine_type: str | None = None
    model: str | None = None
    manufacturer: str | None = None
    serial_number: str | None = None
    line_id: int | None = None
    location: str | None = None
    install_date: date | None = None
    warranty_expiry: date | None = None
    status: str | None = None
    maintenance_interval_hours: int | None = None
    next_maintenance_date: date | None = None
    specifications: dict | None = None
    image_url: str | None = None
    description: str | None = None
    is_active: bool | None = None


class MachineResponse(MachineBase):
    id: int
    current_running_hours: Decimal
    last_maintenance_date: date | None = None
    next_maintenance_date: date | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    line: LineResponse | None = None
    parts_count: int = 0
    critical_parts_count: int = 0

    model_config = {"from_attributes": True}


class MachineListResponse(BaseModel):
    items: list[MachineResponse]
    total: int
    page: int
    page_size: int


class MachineDetailResponse(MachineResponse):
    """Extended machine response with parts and maintenance summary."""
    total_maintenance_count: int = 0
    total_downtime_hours: Decimal = Decimal("0")


# ============== Machine Part ==============
class MachinePartBase(BaseModel):
    material_id: int
    position: str | None = None
    lifetime_hours: Decimal | None = None
    installed_date: date | None = None
    expected_replace_date: date | None = None
    serial_number: str | None = None
    lot_number: str | None = None
    note: str | None = None


class MachinePartCreate(MachinePartBase):
    pass


class MachinePartUpdate(BaseModel):
    position: str | None = None
    current_hours: Decimal | None = None
    lifetime_hours: Decimal | None = None
    expected_replace_date: date | None = None
    serial_number: str | None = None
    lot_number: str | None = None
    note: str | None = None


class MachinePartResponse(MachinePartBase):
    id: int
    machine_id: int
    current_hours: Decimal
    lifetime_percentage: Decimal
    last_replaced_date: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    material_code: str | None = None
    material_name: str | None = None

    model_config = {"from_attributes": True}


class PartReplaceRequest(BaseModel):
    """Request to replace a part on a machine."""
    new_serial_number: str | None = None
    new_lot_number: str | None = None
    note: str | None = None


# ============== Maintenance Log ==============
class MaintenanceLogItemBase(BaseModel):
    material_id: int
    old_part_id: int | None = None
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    action_type: str = "replaced"
    note: str | None = None


class MaintenanceLogItemCreate(MaintenanceLogItemBase):
    pass


class MaintenanceLogItemResponse(MaintenanceLogItemBase):
    id: int
    log_id: int
    material_name: str | None = None
    material_code: str | None = None

    model_config = {"from_attributes": True}


class MaintenanceLogBase(BaseModel):
    machine_id: int
    maintenance_type: str = "corrective"
    maintenance_date: date
    shift: str | None = None
    running_hours_at_time: Decimal | None = None
    description: str
    root_cause: str | None = None
    action_taken: str | None = None
    downtime_hours: Decimal | None = None
    issue_id: int | None = None
    status: str = "completed"


class MaintenanceLogCreate(MaintenanceLogBase):
    items: list[MaintenanceLogItemCreate] = []


class MaintenanceLogUpdate(BaseModel):
    maintenance_type: str | None = None
    maintenance_date: date | None = None
    shift: str | None = None
    running_hours_at_time: Decimal | None = None
    description: str | None = None
    root_cause: str | None = None
    action_taken: str | None = None
    downtime_hours: Decimal | None = None
    issue_id: int | None = None
    status: str | None = None


class MaintenanceLogResponse(MaintenanceLogBase):
    id: int
    log_number: str
    performed_by: int
    created_at: datetime
    performer_name: str | None = None
    machine_name: str | None = None
    machine_code: str | None = None
    items: list[MaintenanceLogItemResponse] = []

    model_config = {"from_attributes": True}


class MaintenanceLogListResponse(BaseModel):
    items: list[MaintenanceLogResponse]
    total: int
    page: int
    page_size: int


# ============== Running Hours ==============
class RunningHourBase(BaseModel):
    record_date: date
    running_hours: Decimal = Field(..., ge=0)
    shift: str | None = None
    note: str | None = None


class RunningHourCreate(RunningHourBase):
    pass


class RunningHourResponse(RunningHourBase):
    id: int
    machine_id: int
    cumulative_hours: Decimal
    recorded_by: int | None = None
    recorder_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============== Parts Tracking / Alerts ==============
class PartLifetimeAlert(BaseModel):
    """Alert for parts nearing end of lifetime."""
    part_id: int
    machine_id: int
    machine_code: str
    machine_name: str
    line_name: str | None = None
    material_id: int
    material_code: str
    material_name: str
    position: str | None = None
    lifetime_hours: Decimal | None = None
    current_hours: Decimal
    lifetime_percentage: Decimal
    installed_date: date | None = None
    expected_replace_date: date | None = None
    status: str  # warning, critical, expired


class LeadTimeAlert(BaseModel):
    """Alert for materials that need ordering based on lead time."""
    material_id: int
    material_code: str
    material_name: str
    supplier_name: str | None = None
    current_stock: Decimal
    min_quantity: Decimal
    lead_time_days: int | None = None
    avg_daily_usage: Decimal | None = None
    days_until_stockout: int | None = None
    reorder_recommended: bool = True


class PartsOverview(BaseModel):
    """Overview statistics for parts tracking."""
    total_parts_installed: int
    active_parts: int
    warning_parts: int  # < 30%
    critical_parts: int  # < 10%
    expired_parts: int  # 0%
    total_machines: int
    running_machines: int
    maintenance_this_month: int
    total_downtime_this_month: Decimal


# ============== Dashboard Extension ==============
class MachineDashboardSummary(BaseModel):
    """Machine-related KPIs for the main dashboard."""
    total_machines: int
    running_machines: int
    broken_machines: int
    parts_critical_count: int  # Parts with < 20% lifetime
    maintenance_this_month: int
    avg_downtime_this_month: Decimal
