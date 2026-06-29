"""Issue (Phiếu xuất kho) schemas."""

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class IssueItemBase(BaseModel):
    material_id: int
    location_id: int | None = None
    quantity: Decimal = Field(..., gt=0)
    lot_number: str | None = None
    serial_number: str | None = None
    note: str | None = None


class IssueItemCreate(IssueItemBase):
    pass


class IssueItemResponse(IssueItemBase):
    id: int
    issue_id: int
    unit_price: Decimal | None = None
    total_price: Decimal | None = None

    model_config = {"from_attributes": True}


class IssueBase(BaseModel):
    issue_date: date
    issue_type: str = "production"  # repair, production, testing, scrap, transfer
    machine: str | None = None
    line: str | None = None
    shift: str | None = None
    receiver: str | None = None
    department: str | None = None
    reason: str | None = None
    work_order: str | None = None
    remark: str | None = None


class IssueCreate(IssueBase):
    items: list[IssueItemCreate] = Field(..., min_length=1)


class IssueUpdate(BaseModel):
    issue_date: date | None = None
    issue_type: str | None = None
    machine: str | None = None
    line: str | None = None
    shift: str | None = None
    receiver: str | None = None
    department: str | None = None
    reason: str | None = None
    work_order: str | None = None
    remark: str | None = None
    items: list[IssueItemCreate] | None = None


class IssueResponse(IssueBase):
    id: int
    issue_number: str
    status: str
    total_amount: Decimal | None = None
    created_by: int
    approved_by: int | None = None
    approved_at: datetime | None = None
    created_at: datetime
    items: list[IssueItemResponse] = []

    model_config = {"from_attributes": True}


class IssueListResponse(BaseModel):
    items: list[IssueResponse]
    total: int
    page: int
    page_size: int
