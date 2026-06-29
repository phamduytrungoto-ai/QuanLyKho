"""Dashboard API endpoints."""

from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.material import Material
from app.models.inventory import Inventory, MaterialMinMax
from app.models.receipt import Receipt
from app.models.issue import Issue
from app.models.warehouse import Location, Warehouse
from app.schemas.dashboard import DashboardSummary, InventoryValueByWarehouse, LowStockItem, RecentActivity
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard summary KPIs."""
    today = date.today()

    # Total materials
    total_mat = await db.execute(select(func.count(Material.id)).where(Material.is_active == True))
    total_materials = total_mat.scalar() or 0

    # Spare parts count
    sp_count = await db.execute(
        select(func.count(Material.id)).where(Material.material_type == "spare_part", Material.is_active == True)
    )
    total_spare_parts = sp_count.scalar() or 0

    # Consumables count
    cons_count = await db.execute(
        select(func.count(Material.id)).where(Material.material_type == "consumable", Material.is_active == True)
    )
    total_consumables = cons_count.scalar() or 0

    # Total inventory value
    inv_value = await db.execute(
        select(func.coalesce(func.sum(Inventory.quantity * Material.price), 0))
        .join(Material)
        .where(Material.price.isnot(None))
    )
    total_inventory_value = inv_value.scalar() or Decimal("0")

    # Low stock count
    low_stock = 0
    mm_result = await db.execute(select(MaterialMinMax))
    for config in mm_result.scalars().all():
        inv_qty = await db.execute(
            select(func.coalesce(func.sum(Inventory.quantity), 0))
            .where(Inventory.material_id == config.material_id)
        )
        qty = inv_qty.scalar() or 0
        if qty <= config.min_quantity:
            low_stock += 1

    # Pending receipts & issues
    pending_r = await db.execute(
        select(func.count(Receipt.id)).where(Receipt.status == "draft")
    )
    pending_receipts = pending_r.scalar() or 0

    pending_i = await db.execute(
        select(func.count(Issue.id)).where(Issue.status == "draft")
    )
    pending_issues = pending_i.scalar() or 0

    # Today's receipts & issues
    today_r = await db.execute(
        select(func.count(Receipt.id)).where(Receipt.receipt_date == today)
    )
    today_receipts = today_r.scalar() or 0

    today_i = await db.execute(
        select(func.count(Issue.id)).where(Issue.issue_date == today)
    )
    today_issues = today_i.scalar() or 0

    return DashboardSummary(
        total_materials=total_materials,
        total_spare_parts=total_spare_parts,
        total_consumables=total_consumables,
        total_inventory_value=total_inventory_value,
        low_stock_count=low_stock,
        pending_receipts=pending_receipts,
        pending_issues=pending_issues,
        today_receipts=today_receipts,
        today_issues=today_issues,
    )


@router.get("/inventory-value", response_model=list[InventoryValueByWarehouse])
async def get_inventory_value_by_warehouse(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get inventory value grouped by warehouse."""
    result = await db.execute(
        select(
            Warehouse.id,
            Warehouse.name,
            func.coalesce(func.sum(Inventory.quantity * Material.price), 0).label("total_value"),
            func.count(func.distinct(Inventory.material_id)).label("total_items"),
        )
        .join(Location, Location.warehouse_id == Warehouse.id)
        .join(Inventory, Inventory.location_id == Location.id)
        .join(Material, Material.id == Inventory.material_id)
        .where(Material.price.isnot(None))
        .group_by(Warehouse.id, Warehouse.name)
    )

    return [
        InventoryValueByWarehouse(
            warehouse_id=row.id,
            warehouse_name=row.name,
            total_value=row.total_value,
            total_items=row.total_items,
        )
        for row in result.all()
    ]


@router.get("/low-stock", response_model=list[LowStockItem])
async def get_low_stock_items(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get materials that are below minimum stock level."""
    mm_result = await db.execute(select(MaterialMinMax))
    items = []

    for config in mm_result.scalars().all():
        inv_qty = await db.execute(
            select(func.coalesce(func.sum(Inventory.quantity), 0))
            .where(Inventory.material_id == config.material_id)
        )
        current_qty = inv_qty.scalar() or Decimal("0")

        if current_qty <= config.min_quantity:
            mat_result = await db.execute(select(Material).where(Material.id == config.material_id))
            material = mat_result.scalar_one_or_none()
            if not material:
                continue

            unit_name = None
            if material.unit:
                unit_name = material.unit.name

            status = "critical" if current_qty == 0 else "warning"
            items.append(LowStockItem(
                material_id=material.id,
                material_code=material.code,
                material_name=material.name,
                material_type=material.material_type,
                current_quantity=current_qty,
                min_quantity=config.min_quantity,
                unit_name=unit_name,
                status=status,
            ))

    items.sort(key=lambda x: (0 if x.status == "critical" else 1, x.current_quantity))
    return items


@router.get("/recent-activities", response_model=list[RecentActivity])
async def get_recent_activities(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent receipt and issue activities."""
    activities = []

    # Recent receipts
    receipts = await db.execute(
        select(Receipt).order_by(Receipt.created_at.desc()).limit(limit)
    )
    for r in receipts.scalars().all():
        activities.append(RecentActivity(
            id=r.id,
            type="receipt",
            number=r.receipt_number,
            date=r.receipt_date.isoformat(),
            status=r.status,
            created_by=r.creator.full_name if r.creator else "Unknown",
            item_count=len(r.items),
        ))

    # Recent issues
    issues = await db.execute(
        select(Issue).order_by(Issue.created_at.desc()).limit(limit)
    )
    for i in issues.scalars().all():
        activities.append(RecentActivity(
            id=i.id,
            type="issue",
            number=i.issue_number,
            date=i.issue_date.isoformat(),
            status=i.status,
            created_by=i.creator.full_name if i.creator else "Unknown",
            item_count=len(i.items),
        ))

    # Sort by date desc
    activities.sort(key=lambda a: a.date, reverse=True)
    return activities[:limit]
