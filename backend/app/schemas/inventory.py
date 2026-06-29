"""Inventory schemas."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.schemas.material import MaterialResponse
from app.schemas.warehouse import LocationResponse


class InventoryResponse(BaseModel):
    id: int
    material_id: int
    location_id: int
    quantity: Decimal
    reserved_quantity: Decimal
    last_updated: datetime
    material: MaterialResponse | None = None
    location: LocationResponse | None = None

    model_config = {"from_attributes": True}


class InventoryListResponse(BaseModel):
    items: list[InventoryResponse]
    total: int
    page: int
    page_size: int


class InventoryAdjustment(BaseModel):
    material_id: int
    location_id: int
    new_quantity: Decimal
    reason: str


class InventoryTransactionResponse(BaseModel):
    id: int
    inventory_id: int
    transaction_type: str
    quantity: Decimal
    balance_after: Decimal
    reference_type: str | None = None
    reference_id: int | None = None
    note: str | None = None
    user_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============== Min-Max ==============
class MinMaxBase(BaseModel):
    material_id: int
    warehouse_id: int | None = None
    min_quantity: Decimal = Field(default=0)
    max_quantity: Decimal = Field(default=0)
    reorder_point: Decimal | None = None
    reorder_quantity: Decimal | None = None
    avg_daily_usage: Decimal | None = None


class MinMaxCreate(MinMaxBase):
    pass


class MinMaxUpdate(BaseModel):
    min_quantity: Decimal | None = None
    max_quantity: Decimal | None = None
    reorder_point: Decimal | None = None
    reorder_quantity: Decimal | None = None
    avg_daily_usage: Decimal | None = None


class MinMaxResponse(MinMaxBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryAlert(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    warehouse_id: int | None = None
    warehouse_name: str | None = None
    current_quantity: Decimal
    min_quantity: Decimal
    max_quantity: Decimal
    status: str  # "below_min", "above_max", "at_reorder_point", "ok"
    lead_time_days: int | None = None
    avg_daily_usage: Decimal | None = None
    days_until_stockout: int | None = None
