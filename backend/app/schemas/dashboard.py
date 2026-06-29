"""Dashboard schemas."""

from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_materials: int = 0
    total_spare_parts: int = 0
    total_consumables: int = 0
    total_inventory_value: Decimal = Decimal("0")
    low_stock_count: int = 0
    pending_receipts: int = 0
    pending_issues: int = 0
    today_receipts: int = 0
    today_issues: int = 0


class InventoryValueByWarehouse(BaseModel):
    warehouse_id: int
    warehouse_name: str
    total_value: Decimal
    total_items: int


class LowStockItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    material_type: str
    current_quantity: Decimal
    min_quantity: Decimal
    unit_name: str | None = None
    status: str  # "critical", "warning"


class RecentActivity(BaseModel):
    id: int
    type: str  # "receipt", "issue"
    number: str
    date: str
    status: str
    created_by: str
    item_count: int
