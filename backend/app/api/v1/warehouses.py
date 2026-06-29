"""Warehouses and Locations API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.warehouse import Warehouse, Location
from app.schemas.warehouse import (
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    LocationCreate, LocationUpdate, LocationResponse,
)
from app.core.permissions import require_permission, Permission
from app.core.security import get_current_active_user

router = APIRouter()


# ============== Warehouses ==============
@router.get("", response_model=list[WarehouseResponse])
async def list_warehouses(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all warehouses."""
    result = await db.execute(select(Warehouse).where(Warehouse.is_active == True).order_by(Warehouse.code))
    return [WarehouseResponse.model_validate(w) for w in result.scalars().all()]


@router.post("", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(
    data: WarehouseCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new warehouse."""
    existing = await db.execute(select(Warehouse).where(Warehouse.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Warehouse code '{data.code}' already exists")

    warehouse = Warehouse(**data.model_dump())
    db.add(warehouse)
    await db.flush()
    await db.refresh(warehouse)
    return WarehouseResponse.model_validate(warehouse)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific warehouse with its locations."""
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return WarehouseResponse.model_validate(warehouse)


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    data: WarehouseUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a warehouse."""
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)
    await db.flush()
    await db.refresh(warehouse)
    return WarehouseResponse.model_validate(warehouse)


@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: int,
    current_user: User = Depends(require_permission(Permission.DELETE)),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a warehouse."""
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    warehouse.is_active = False
    await db.flush()


# ============== Locations ==============
@router.get("/{warehouse_id}/locations", response_model=list[LocationResponse])
async def list_locations(
    warehouse_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all locations in a warehouse."""
    result = await db.execute(
        select(Location)
        .where(Location.warehouse_id == warehouse_id, Location.is_active == True)
        .order_by(Location.code)
    )
    return [LocationResponse.model_validate(loc) for loc in result.scalars().all()]


@router.post("/{warehouse_id}/locations", response_model=LocationResponse, status_code=201)
async def create_location(
    warehouse_id: int,
    data: LocationCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new location in a warehouse."""
    # Verify warehouse exists
    wh = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = wh.scalar_one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Check duplicate code
    existing = await db.execute(select(Location).where(Location.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Location code '{data.code}' already exists")

    # Build full path
    parts = [warehouse.name]
    if data.rack:
        parts.append(f"Kệ {data.rack}")
    if data.level:
        parts.append(f"Tầng {data.level}")
    if data.bin:
        parts.append(f"Ô {data.bin}")
    full_path = " > ".join(parts)

    location = Location(
        warehouse_id=warehouse_id,
        code=data.code,
        rack=data.rack,
        level=data.level,
        bin=data.bin,
        full_path=full_path,
        description=data.description,
    )
    db.add(location)
    await db.flush()
    await db.refresh(location)
    return LocationResponse.model_validate(location)


@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    data: LocationUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a location."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    await db.flush()
    await db.refresh(location)
    return LocationResponse.model_validate(location)
