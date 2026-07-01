from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal

# Báo cáo Nhập-Xuất-Tồn (Inventory Valuation)
class InventoryValuationItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    unit: str
    opening_stock: Decimal
    opening_value: Decimal
    inward_qty: Decimal
    inward_value: Decimal
    outward_qty: Decimal
    outward_value: Decimal
    closing_stock: Decimal
    closing_value: Decimal

class InventoryValuationReport(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    warehouse_id: Optional[int]
    items: List[InventoryValuationItem]
    total_opening_value: Decimal
    total_inward_value: Decimal
    total_outward_value: Decimal
    total_closing_value: Decimal

# Thẻ Kho (Stock Card)
class StockCardItem(BaseModel):
    transaction_date: date
    transaction_type: str # 'receipt' | 'issue' | 'opening' | 'closing'
    reference_number: Optional[str]
    inward_qty: Decimal
    outward_qty: Decimal
    balance: Decimal
    note: Optional[str]

class StockCardReport(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    unit: str
    start_date: Optional[date]
    end_date: Optional[date]
    warehouse_id: Optional[int]
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: List[StockCardItem]

# Phân tích ABC (ABC Analysis)
class AbcAnalysisItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    unit: str
    total_usage_qty: Decimal
    total_usage_value: Decimal
    cumulative_value: Decimal
    cumulative_percentage: Decimal
    abc_class: str # 'A', 'B', 'C'

class AbcAnalysisReport(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    items: List[AbcAnalysisItem]
    summary_a: int
    summary_b: int
    summary_c: int

# Chi phí bảo trì (Maintenance Cost)
class MaintenanceCostItem(BaseModel):
    machine_id: int
    machine_code: str
    machine_name: str
    line_name: Optional[str]
    maintenance_count: int
    total_downtime: Decimal
    parts_replaced_count: int
    total_cost: Decimal

class MaintenanceCostReport(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    items: List[MaintenanceCostItem]
    total_overall_cost: Decimal
