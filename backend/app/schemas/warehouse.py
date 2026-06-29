"""Warehouse and Location schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


# ============== Location ==============
class LocationBase(BaseModel):
    code: str = Field(..., max_length=30)
    rack: str | None = None
    level: str | None = None
    bin: str | None = None
    description: str | None = None


class LocationCreate(LocationBase):
    warehouse_id: int


class LocationUpdate(BaseModel):
    rack: str | None = None
    level: str | None = None
    bin: str | None = None
    description: str | None = None
    is_active: bool | None = None


class LocationResponse(LocationBase):
    id: int
    warehouse_id: int
    full_path: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============== Warehouse ==============
class WarehouseBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    name_en: str | None = None
    description: str | None = None
    warehouse_type: str = "main"
    address: str | None = None
    manager: str | None = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = None
    name_en: str | None = None
    description: str | None = None
    warehouse_type: str | None = None
    address: str | None = None
    manager: str | None = None
    is_active: bool | None = None


class WarehouseResponse(WarehouseBase):
    id: int
    is_active: bool
    created_at: datetime
    locations: list[LocationResponse] = []

    model_config = {"from_attributes": True}
