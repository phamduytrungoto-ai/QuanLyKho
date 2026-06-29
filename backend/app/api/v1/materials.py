"""Materials API endpoints including Categories, Units, and Suppliers."""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.material import Material, MaterialCategory, Unit, Supplier, MaterialImage
from app.schemas.material import (
    MaterialCreate, MaterialUpdate, MaterialResponse, MaterialListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    UnitCreate, UnitResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
)
from app.core.permissions import require_permission, Permission
from app.core.security import get_current_active_user

router = APIRouter()


# ============== Categories ==============
@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all material categories."""
    result = await db.execute(select(MaterialCategory).order_by(MaterialCategory.code))
    return [CategoryResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new material category."""
    existing = await db.execute(select(MaterialCategory).where(MaterialCategory.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Category code '{data.code}' already exists")

    category = MaterialCategory(**data.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a material category."""
    result = await db.execute(select(MaterialCategory).where(MaterialCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    await db.flush()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_permission(Permission.DELETE)),
    db: AsyncSession = Depends(get_db),
):
    """Delete a material category."""
    result = await db.execute(select(MaterialCategory).where(MaterialCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.is_active = False
    await db.flush()


# ============== Units ==============
@router.get("/units", response_model=list[UnitResponse])
async def list_units(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all units of measurement."""
    result = await db.execute(select(Unit).order_by(Unit.code))
    return [UnitResponse.model_validate(u) for u in result.scalars().all()]


@router.post("/units", response_model=UnitResponse, status_code=201)
async def create_unit(
    data: UnitCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new unit of measurement."""
    existing = await db.execute(select(Unit).where(Unit.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Unit code '{data.code}' already exists")
    unit = Unit(**data.model_dump())
    db.add(unit)
    await db.flush()
    await db.refresh(unit)
    return UnitResponse.model_validate(unit)


# ============== Suppliers ==============
@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all suppliers."""
    query = select(Supplier).where(Supplier.is_active == True).order_by(Supplier.code)
    if search:
        query = query.where((Supplier.name.ilike(f"%{search}%")) | (Supplier.code.ilike(f"%{search}%")))
    result = await db.execute(query)
    return [SupplierResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    data: SupplierCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new supplier."""
    existing = await db.execute(select(Supplier).where(Supplier.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Supplier code '{data.code}' already exists")
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a supplier."""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    await db.flush()
    await db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)


# ============== Materials ==============
@router.get("", response_model=MaterialListResponse)
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    material_type: str | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List materials with pagination, search, and filters."""
    query = select(Material)
    count_query = select(func.count(Material.id))

    # Filters
    if search:
        search_filter = (
            (Material.code.ilike(f"%{search}%"))
            | (Material.name.ilike(f"%{search}%"))
            | (Material.barcode.ilike(f"%{search}%"))
            | (Material.name_en.ilike(f"%{search}%"))
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    if material_type:
        query = query.where(Material.material_type == material_type)
        count_query = count_query.where(Material.material_type == material_type)
    if category_id:
        query = query.where(Material.category_id == category_id)
        count_query = count_query.where(Material.category_id == category_id)
    if supplier_id:
        query = query.where(Material.supplier_id == supplier_id)
        count_query = count_query.where(Material.supplier_id == supplier_id)
    if status:
        query = query.where(Material.status == status)
        count_query = count_query.where(Material.status == status)

    # Count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.order_by(Material.code).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    materials = result.scalars().all()

    return MaterialListResponse(
        items=[MaterialResponse.model_validate(m) for m in materials],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=MaterialResponse, status_code=201)
async def create_material(
    data: MaterialCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new material."""
    existing = await db.execute(select(Material).where(Material.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Material code '{data.code}' already exists")

    if data.barcode:
        barcode_check = await db.execute(select(Material).where(Material.barcode == data.barcode))
        if barcode_check.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"Barcode '{data.barcode}' already exists")

    material = Material(**data.model_dump())
    db.add(material)
    await db.flush()
    await db.refresh(material)
    return MaterialResponse.model_validate(material)


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific material by ID."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialResponse.model_validate(material)


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    data: MaterialUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a material."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(material, field, value)
    await db.flush()
    await db.refresh(material)
    return MaterialResponse.model_validate(material)


@router.delete("/{material_id}", status_code=204)
async def delete_material(
    material_id: int,
    current_user: User = Depends(require_permission(Permission.DELETE)),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a material."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    material.is_active = False
    material.status = "inactive"
    await db.flush()
