"""Parts Tracking & Alerts API endpoints (Phase 2)."""

from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.machine import (
    Machine, MachinePart, MaintenanceLog, ProductionLine,
)
from app.models.material import Material
from app.models.inventory import Inventory, MaterialMinMax
from app.schemas.machine import (
    PartLifetimeAlert, LeadTimeAlert, PartsOverview, MachineDashboardSummary,
)
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/lifetime-alerts", response_model=list[PartLifetimeAlert])
async def get_lifetime_alerts(
    threshold: int = Query(30, ge=0, le=100, description="Percentage threshold"),
    line_id: int | None = None,
    machine_id: int | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get parts that have lifetime remaining below the threshold percentage."""
    query = select(MachinePart).where(
        MachinePart.status.in_(["active", "warning", "critical", "expired"]),
        MachinePart.lifetime_percentage <= threshold,
    )

    if machine_id:
        query = query.where(MachinePart.machine_id == machine_id)

    if line_id:
        query = query.join(Machine, Machine.id == MachinePart.machine_id).where(Machine.line_id == line_id)

    query = query.order_by(MachinePart.lifetime_percentage)
    result = await db.execute(query)
    parts = result.scalars().all()

    alerts = []
    for part in parts:
        machine = part.machine
        alerts.append(PartLifetimeAlert(
            part_id=part.id,
            machine_id=part.machine_id,
            machine_code=machine.code if machine else "",
            machine_name=machine.name if machine else "",
            line_name=machine.line.name if machine and machine.line else None,
            material_id=part.material_id,
            material_code=part.material.code if part.material else "",
            material_name=part.material.name if part.material else "",
            position=part.position,
            lifetime_hours=part.lifetime_hours,
            current_hours=part.current_hours,
            lifetime_percentage=part.lifetime_percentage,
            installed_date=part.installed_date,
            expected_replace_date=part.expected_replace_date,
            status=part.status,
        ))

    return alerts


@router.get("/lead-time-alerts", response_model=list[LeadTimeAlert])
async def get_lead_time_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get materials that need ordering based on low stock and lead time."""
    mm_result = await db.execute(select(MaterialMinMax))
    alerts = []

    for config in mm_result.scalars().all():
        # Get current stock
        inv_qty = await db.execute(
            select(func.coalesce(func.sum(Inventory.quantity), 0))
            .where(Inventory.material_id == config.material_id)
        )
        current_stock = inv_qty.scalar() or Decimal("0")

        if current_stock <= (config.reorder_point or config.min_quantity):
            mat_result = await db.execute(
                select(Material).where(Material.id == config.material_id)
            )
            material = mat_result.scalar_one_or_none()
            if not material:
                continue

            lead_time = material.lead_time_days
            avg_usage = config.avg_daily_usage

            days_until_stockout = None
            if avg_usage and avg_usage > 0:
                days_until_stockout = int(current_stock / avg_usage)

            supplier_name = material.supplier.name if material.supplier else None

            alerts.append(LeadTimeAlert(
                material_id=material.id,
                material_code=material.code,
                material_name=material.name,
                supplier_name=supplier_name,
                current_stock=current_stock,
                min_quantity=config.min_quantity,
                lead_time_days=lead_time,
                avg_daily_usage=avg_usage,
                days_until_stockout=days_until_stockout,
                reorder_recommended=True,
            ))

    # Sort by urgency: lowest days_until_stockout first
    alerts.sort(key=lambda a: (a.days_until_stockout or 0))
    return alerts


@router.get("/overview", response_model=PartsOverview)
async def get_parts_overview(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get overview statistics for parts tracking."""
    today = date.today()
    first_of_month = today.replace(day=1)

    # Parts counts
    total_parts = await db.execute(
        select(func.count(MachinePart.id)).where(MachinePart.status != "replaced")
    )
    active_parts = await db.execute(
        select(func.count(MachinePart.id)).where(MachinePart.status == "active")
    )
    warning_parts = await db.execute(
        select(func.count(MachinePart.id)).where(MachinePart.status == "warning")
    )
    critical_parts = await db.execute(
        select(func.count(MachinePart.id)).where(MachinePart.status == "critical")
    )
    expired_parts = await db.execute(
        select(func.count(MachinePart.id)).where(MachinePart.status == "expired")
    )

    # Machine counts
    total_machines = await db.execute(
        select(func.count(Machine.id)).where(Machine.is_active == True)
    )
    running_machines = await db.execute(
        select(func.count(Machine.id)).where(Machine.is_active == True, Machine.status == "running")
    )

    # Maintenance this month
    maint_month = await db.execute(
        select(func.count(MaintenanceLog.id))
        .where(MaintenanceLog.maintenance_date >= first_of_month)
    )
    downtime_month = await db.execute(
        select(func.coalesce(func.sum(MaintenanceLog.downtime_hours), 0))
        .where(MaintenanceLog.maintenance_date >= first_of_month)
    )

    return PartsOverview(
        total_parts_installed=total_parts.scalar() or 0,
        active_parts=active_parts.scalar() or 0,
        warning_parts=warning_parts.scalar() or 0,
        critical_parts=critical_parts.scalar() or 0,
        expired_parts=expired_parts.scalar() or 0,
        total_machines=total_machines.scalar() or 0,
        running_machines=running_machines.scalar() or 0,
        maintenance_this_month=maint_month.scalar() or 0,
        total_downtime_this_month=downtime_month.scalar() or Decimal("0"),
    )


@router.get("/dashboard-summary", response_model=MachineDashboardSummary)
async def get_machine_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Machine-related KPIs for the main dashboard."""
    today = date.today()
    first_of_month = today.replace(day=1)

    total_machines = await db.execute(
        select(func.count(Machine.id)).where(Machine.is_active == True)
    )
    running_machines = await db.execute(
        select(func.count(Machine.id)).where(Machine.is_active == True, Machine.status == "running")
    )
    broken_machines = await db.execute(
        select(func.count(Machine.id)).where(Machine.is_active == True, Machine.status == "broken")
    )
    critical_parts = await db.execute(
        select(func.count(MachinePart.id)).where(
            MachinePart.status.in_(["critical", "expired"]),
        )
    )
    maint_month = await db.execute(
        select(func.count(MaintenanceLog.id))
        .where(MaintenanceLog.maintenance_date >= first_of_month)
    )
    avg_downtime = await db.execute(
        select(func.coalesce(func.avg(MaintenanceLog.downtime_hours), 0))
        .where(MaintenanceLog.maintenance_date >= first_of_month)
    )

    return MachineDashboardSummary(
        total_machines=total_machines.scalar() or 0,
        running_machines=running_machines.scalar() or 0,
        broken_machines=broken_machines.scalar() or 0,
        parts_critical_count=critical_parts.scalar() or 0,
        maintenance_this_month=maint_month.scalar() or 0,
        avg_downtime_this_month=avg_downtime.scalar() or Decimal("0"),
    )
