"""Inventory tracking API endpoints."""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.inventory import Inventory, InventoryTransaction, MaterialMinMax
from app.models.material import Material
from app.models.warehouse import Location, Warehouse
from app.schemas.inventory import (
    InventoryResponse, InventoryListResponse, InventoryAdjustment,
    InventoryTransactionResponse, MinMaxCreate, MinMaxUpdate, MinMaxResponse, InventoryAlert,
)
from app.core.permissions import require_permission, Permission
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("", response_model=InventoryListResponse)
async def list_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: int | None = None,
    material_type: str | None = None,
    search: str | None = None,
    low_stock_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List inventory records with filters."""
    query = select(Inventory).join(Material).join(Location)
    count_query = select(func.count(Inventory.id)).join(Material).join(Location)

    if warehouse_id:
        query = query.where(Location.warehouse_id == warehouse_id)
        count_query = count_query.where(Location.warehouse_id == warehouse_id)
    if material_type:
        query = query.where(Material.material_type == material_type)
        count_query = count_query.where(Material.material_type == material_type)
    if search:
        search_filter = (Material.code.ilike(f"%{search}%")) | (Material.name.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Material.code).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return InventoryListResponse(
        items=[InventoryResponse.model_validate(inv) for inv in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/adjust")
async def adjust_inventory(
    data: InventoryAdjustment,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Manually adjust inventory quantity (for stocktake)."""
    result = await db.execute(
        select(Inventory).where(
            Inventory.material_id == data.material_id,
            Inventory.location_id == data.location_id,
        )
    )
    inv = result.scalar_one_or_none()

    if not inv:
        # Create new inventory record
        inv = Inventory(
            material_id=data.material_id,
            location_id=data.location_id,
            quantity=data.new_quantity,
        )
        db.add(inv)
        await db.flush()
        await db.refresh(inv)
    else:
        old_qty = inv.quantity
        inv.quantity = data.new_quantity
        await db.flush()

    # Log transaction
    transaction = InventoryTransaction(
        inventory_id=inv.id,
        transaction_type="adjustment",
        quantity=data.new_quantity - (old_qty if 'old_qty' in dir() else Decimal("0")),
        balance_after=data.new_quantity,
        reference_type="adjustment",
        note=data.reason,
        user_id=current_user.id,
    )
    db.add(transaction)
    await db.flush()

    return {"message": "Inventory adjusted", "new_quantity": str(data.new_quantity)}


@router.get("/transactions", response_model=list[InventoryTransactionResponse])
async def list_transactions(
    material_id: int | None = None,
    location_id: int | None = None,
    transaction_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List inventory transactions (movement history)."""
    query = select(InventoryTransaction).join(Inventory)
    if material_id:
        query = query.where(Inventory.material_id == material_id)
    if location_id:
        query = query.where(Inventory.location_id == location_id)
    if transaction_type:
        query = query.where(InventoryTransaction.transaction_type == transaction_type)

    query = query.order_by(InventoryTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [InventoryTransactionResponse.model_validate(t) for t in result.scalars().all()]


# ============== Min-Max ==============
@router.get("/alerts", response_model=list[InventoryAlert])
async def get_inventory_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get inventory alerts (items below min or above max)."""
    # Get all min-max configs
    result = await db.execute(select(MaterialMinMax))
    configs = result.scalars().all()

    alerts = []
    for config in configs:
        # Get total quantity for this material in the relevant warehouse
        inv_query = select(func.coalesce(func.sum(Inventory.quantity), 0)).join(Location)
        inv_query = inv_query.where(Inventory.material_id == config.material_id)
        if config.warehouse_id:
            inv_query = inv_query.where(Location.warehouse_id == config.warehouse_id)

        inv_result = await db.execute(inv_query)
        current_qty = inv_result.scalar() or Decimal("0")

        # Determine status
        if current_qty <= config.min_quantity:
            status = "below_min"
        elif current_qty >= config.max_quantity:
            status = "above_max"
        elif config.reorder_point and current_qty <= config.reorder_point:
            status = "at_reorder_point"
        else:
            continue  # No alert needed

        # Get material info
        mat_result = await db.execute(select(Material).where(Material.id == config.material_id))
        material = mat_result.scalar_one_or_none()
        if not material:
            continue

        # Get warehouse name
        wh_name = None
        if config.warehouse_id:
            wh_result = await db.execute(select(Warehouse).where(Warehouse.id == config.warehouse_id))
            wh = wh_result.scalar_one_or_none()
            wh_name = wh.name if wh else None

        # Calculate days until stockout
        days_until = None
        if config.avg_daily_usage and config.avg_daily_usage > 0:
            days_until = int(current_qty / config.avg_daily_usage)

        alerts.append(InventoryAlert(
            material_id=config.material_id,
            material_code=material.code,
            material_name=material.name,
            warehouse_id=config.warehouse_id,
            warehouse_name=wh_name,
            current_quantity=current_qty,
            min_quantity=config.min_quantity,
            max_quantity=config.max_quantity,
            status=status,
            lead_time_days=material.lead_time_days,
            avg_daily_usage=config.avg_daily_usage,
            days_until_stockout=days_until,
        ))

    # Sort: below_min first, then at_reorder_point
    priority = {"below_min": 0, "at_reorder_point": 1, "above_max": 2}
    alerts.sort(key=lambda a: priority.get(a.status, 3))

    return alerts


@router.get("/min-max", response_model=list[MinMaxResponse])
async def list_min_max(
    material_id: int | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List Min-Max configurations."""
    query = select(MaterialMinMax)
    if material_id:
        query = query.where(MaterialMinMax.material_id == material_id)
    result = await db.execute(query)
    return [MinMaxResponse.model_validate(mm) for mm in result.scalars().all()]


@router.post("/min-max", response_model=MinMaxResponse, status_code=201)
async def create_min_max(
    data: MinMaxCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a Min-Max configuration."""
    mm = MaterialMinMax(**data.model_dump())
    db.add(mm)
    await db.flush()
    await db.refresh(mm)
    return MinMaxResponse.model_validate(mm)


@router.put("/min-max/{min_max_id}", response_model=MinMaxResponse)
async def update_min_max(
    min_max_id: int,
    data: MinMaxUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a Min-Max configuration."""
    result = await db.execute(select(MaterialMinMax).where(MaterialMinMax.id == min_max_id))
    mm = result.scalar_one_or_none()
    if not mm:
        raise HTTPException(status_code=404, detail="Min-Max config not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mm, field, value)
    await db.flush()
    await db.refresh(mm)
    return MinMaxResponse.model_validate(mm)
