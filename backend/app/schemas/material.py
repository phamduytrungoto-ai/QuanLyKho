"""Material, Category, Unit, Supplier schemas."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# ============== Category ==============
class CategoryBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    name_en: str | None = None
    name_ja: str | None = None
    description: str | None = None
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    name_en: str | None = None
    name_ja: str | None = None
    description: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============== Unit ==============
class UnitBase(BaseModel):
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=50)
    name_en: str | None = None
    name_ja: str | None = None


class UnitCreate(UnitBase):
    pass


class UnitResponse(UnitBase):
    id: int

    model_config = {"from_attributes": True}


# ============== Supplier ==============
class SupplierBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    name_en: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tax_code: str | None = None
    lead_time_days: int | None = None
    payment_terms: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = None
    name_en: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tax_code: str | None = None
    lead_time_days: int | None = None
    payment_terms: str | None = None
    is_active: bool | None = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============== Material ==============
class MaterialImageResponse(BaseModel):
    id: int
    image_url: str
    is_primary: bool

    model_config = {"from_attributes": True}


class MaterialBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    name_ja: str | None = None
    name_en: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    model: str | None = None
    manufacturer: str | None = None
    supplier_id: int | None = None
    category_id: int | None = None
    unit_id: int | None = None
    material_type: str = "spare_part"
    price: Decimal | None = None
    currency: str = "VND"
    lifetime_hours: int | None = None
    lead_time_days: int | None = None
    moq: int | None = None
    specifications: dict | None = None
    datasheet_url: str | None = None
    description: str | None = None
    consumption_rate: Decimal | None = None
    consumption_unit: str | None = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str | None = None
    name_ja: str | None = None
    name_en: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    model: str | None = None
    manufacturer: str | None = None
    supplier_id: int | None = None
    category_id: int | None = None
    unit_id: int | None = None
    material_type: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    lifetime_hours: int | None = None
    lead_time_days: int | None = None
    moq: int | None = None
    specifications: dict | None = None
    datasheet_url: str | None = None
    description: str | None = None
    consumption_rate: Decimal | None = None
    consumption_unit: str | None = None
    status: str | None = None
    is_active: bool | None = None


class MaterialResponse(MaterialBase):
    id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse | None = None
    unit: UnitResponse | None = None
    supplier: SupplierResponse | None = None
    images: list[MaterialImageResponse] = []

    model_config = {"from_attributes": True}


class MaterialListResponse(BaseModel):
    items: list[MaterialResponse]
    total: int
    page: int
    page_size: int
