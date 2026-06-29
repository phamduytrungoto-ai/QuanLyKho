"""Receipt (Phiếu nhập kho) schemas."""

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ReceiptItemBase(BaseModel):
    material_id: int
    location_id: int | None = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal | None = None
    lot_number: str | None = None
    serial_number: str | None = None
    expiry_date: date | None = None
    note: str | None = None


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItemResponse(ReceiptItemBase):
    id: int
    receipt_id: int
    total_price: Decimal | None = None

    model_config = {"from_attributes": True}


class ReceiptBase(BaseModel):
    receipt_date: date
    receipt_type: str = "purchase"  # purchase, repair_return, transfer, return, stocktake
    supplier_id: int | None = None
    po_number: str | None = None
    invoice_number: str | None = None
    note: str | None = None


class ReceiptCreate(ReceiptBase):
    items: list[ReceiptItemCreate] = Field(..., min_length=1)


class ReceiptUpdate(BaseModel):
    receipt_date: date | None = None
    receipt_type: str | None = None
    supplier_id: int | None = None
    po_number: str | None = None
    invoice_number: str | None = None
    note: str | None = None
    items: list[ReceiptItemCreate] | None = None


class ReceiptResponse(ReceiptBase):
    id: int
    receipt_number: str
    status: str
    total_amount: Decimal | None = None
    created_by: int
    approved_by: int | None = None
    approved_at: datetime | None = None
    created_at: datetime
    items: list[ReceiptItemResponse] = []

    model_config = {"from_attributes": True}


class ReceiptListResponse(BaseModel):
    items: list[ReceiptResponse]
    total: int
    page: int
    page_size: int
