"""Machines, Production Lines, Parts, Maintenance, Running Hours API endpoints (Phase 2)."""

from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.machine import (
    ProductionLine, Machine, MachinePart,
    MaintenanceLog, MaintenanceLogItem, MachineRunningHour,
)
from app.schemas.machine import (
    LineCreate, LineUpdate, LineResponse,
    MachineCreate, MachineUpdate, MachineResponse, MachineListResponse, MachineDetailResponse,
    MachinePartCreate, MachinePartUpdate, MachinePartResponse, PartReplaceRequest,
    MaintenanceLogCreate, MaintenanceLogUpdate, MaintenanceLogResponse, MaintenanceLogListResponse,
    MaintenanceLogItemResponse,
    RunningHourCreate, RunningHourResponse,
)
from app.core.permissions import require_permission, Permission
from app.core.security import get_current_active_user

router = APIRouter()


# ===================== PRODUCTION LINES =====================

@router.get("/lines", response_model=list[LineResponse])
async def list_lines(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all production lines."""
    result = await db.execute(
        select(ProductionLine).order_by(ProductionLine.code)
    )
    return [LineResponse.model_validate(l) for l in result.scalars().all()]


@router.post("/lines", response_model=LineResponse, status_code=201)
async def create_line(
    data: LineCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new production line."""
    existing = await db.execute(select(ProductionLine).where(ProductionLine.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Line with code '{data.code}' already exists")

    line = ProductionLine(**data.model_dump())
    db.add(line)
    await db.flush()
    await db.refresh(line)
    return LineResponse.model_validate(line)


@router.put("/lines/{line_id}", response_model=LineResponse)
async def update_line(
    line_id: int,
    data: LineUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a production line."""
    result = await db.execute(select(ProductionLine).where(ProductionLine.id == line_id))
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(404, "Production line not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(line, field, value)

    await db.flush()
    await db.refresh(line)
    return LineResponse.model_validate(line)


# ===================== MACHINES =====================

def _build_machine_response(machine: Machine) -> MachineResponse:
    """Build MachineResponse with computed fields."""
    parts = machine.parts or []
    critical_parts = sum(1 for p in parts if p.status in ("critical", "expired"))
    resp = MachineResponse.model_validate(machine)
    resp.parts_count = len(parts)
    resp.critical_parts_count = critical_parts
    return resp


@router.get("", response_model=MachineListResponse)
async def list_machines(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    line_id: int | None = None,
    machine_type: str | None = None,
    status: str | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List machines with filters."""
    query = select(Machine).where(Machine.is_active == True)
    count_query = select(func.count(Machine.id)).where(Machine.is_active == True)

    if line_id:
        query = query.where(Machine.line_id == line_id)
        count_query = count_query.where(Machine.line_id == line_id)
    if machine_type:
        query = query.where(Machine.machine_type == machine_type)
        count_query = count_query.where(Machine.machine_type == machine_type)
    if status:
        query = query.where(Machine.status == status)
        count_query = count_query.where(Machine.status == status)
    if search:
        search_filter = (
            Machine.code.ilike(f"%{search}%")
            | Machine.name.ilike(f"%{search}%")
            | Machine.serial_number.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Machine.code).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    machines = result.scalars().all()

    return MachineListResponse(
        items=[_build_machine_response(m) for m in machines],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=MachineResponse, status_code=201)
async def create_machine(
    data: MachineCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new machine."""
    existing = await db.execute(select(Machine).where(Machine.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Machine with code '{data.code}' already exists")

    machine = Machine(**data.model_dump())
    db.add(machine)
    await db.flush()
    await db.refresh(machine)
    return _build_machine_response(machine)


@router.get("/{machine_id}", response_model=MachineDetailResponse)
async def get_machine(
    machine_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get machine detail with summary stats."""
    result = await db.execute(select(Machine).where(Machine.id == machine_id))
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(404, "Machine not found")

    parts = machine.parts or []
    critical_parts = sum(1 for p in parts if p.status in ("critical", "expired"))
    logs = machine.maintenance_logs or []
    total_downtime = sum((log.downtime_hours or Decimal("0")) for log in logs)

    resp = MachineDetailResponse.model_validate(machine)
    resp.parts_count = len(parts)
    resp.critical_parts_count = critical_parts
    resp.total_maintenance_count = len(logs)
    resp.total_downtime_hours = total_downtime
    return resp


@router.put("/{machine_id}", response_model=MachineResponse)
async def update_machine(
    machine_id: int,
    data: MachineUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a machine."""
    result = await db.execute(select(Machine).where(Machine.id == machine_id))
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(404, "Machine not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)

    await db.flush()
    await db.refresh(machine)
    return _build_machine_response(machine)


# ===================== MACHINE PARTS =====================

@router.get("/{machine_id}/parts", response_model=list[MachinePartResponse])
async def list_machine_parts(
    machine_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List parts installed on a machine."""
    result = await db.execute(
        select(MachinePart)
        .where(MachinePart.machine_id == machine_id, MachinePart.status != "replaced")
        .order_by(MachinePart.lifetime_percentage)
    )
    parts = result.scalars().all()

    responses = []
    for part in parts:
        resp = MachinePartResponse.model_validate(part)
        if part.material:
            resp.material_code = part.material.code
            resp.material_name = part.material.name
        responses.append(resp)
    return responses


@router.post("/{machine_id}/parts", response_model=MachinePartResponse, status_code=201)
async def install_part(
    machine_id: int,
    data: MachinePartCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Install a new part on a machine."""
    # Verify machine exists
    machine_result = await db.execute(select(Machine).where(Machine.id == machine_id))
    if not machine_result.scalar_one_or_none():
        raise HTTPException(404, "Machine not found")

    part = MachinePart(
        machine_id=machine_id,
        material_id=data.material_id,
        position=data.position,
        lifetime_hours=data.lifetime_hours,
        current_hours=Decimal("0"),
        lifetime_percentage=Decimal("100"),
        installed_date=data.installed_date or date.today(),
        expected_replace_date=data.expected_replace_date,
        serial_number=data.serial_number,
        lot_number=data.lot_number,
        note=data.note,
        status="active",
    )
    db.add(part)
    await db.flush()
    await db.refresh(part)

    resp = MachinePartResponse.model_validate(part)
    if part.material:
        resp.material_code = part.material.code
        resp.material_name = part.material.name
    return resp


@router.put("/{machine_id}/parts/{part_id}", response_model=MachinePartResponse)
async def update_part(
    machine_id: int,
    part_id: int,
    data: MachinePartUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a part's info (hours, position, etc.)."""
    result = await db.execute(
        select(MachinePart).where(MachinePart.id == part_id, MachinePart.machine_id == machine_id)
    )
    part = result.scalar_one_or_none()
    if not part:
        raise HTTPException(404, "Part not found on this machine")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(part, field, value)

    # Recalculate lifetime percentage
    if part.lifetime_hours and part.lifetime_hours > 0:
        remaining = max(Decimal("0"), part.lifetime_hours - part.current_hours)
        part.lifetime_percentage = round((remaining / part.lifetime_hours) * 100, 2)

        if part.lifetime_percentage <= 0:
            part.status = "expired"
        elif part.lifetime_percentage <= 10:
            part.status = "critical"
        elif part.lifetime_percentage <= 30:
            part.status = "warning"
        else:
            part.status = "active"

    await db.flush()
    await db.refresh(part)

    resp = MachinePartResponse.model_validate(part)
    if part.material:
        resp.material_code = part.material.code
        resp.material_name = part.material.name
    return resp


@router.post("/{machine_id}/parts/{part_id}/replace", response_model=MachinePartResponse)
async def replace_part(
    machine_id: int,
    part_id: int,
    data: PartReplaceRequest,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Replace a part: mark old as replaced, create new with reset hours."""
    result = await db.execute(
        select(MachinePart).where(MachinePart.id == part_id, MachinePart.machine_id == machine_id)
    )
    old_part = result.scalar_one_or_none()
    if not old_part:
        raise HTTPException(404, "Part not found on this machine")

    # Mark old part as replaced
    old_part.status = "replaced"
    old_part.last_replaced_date = date.today()

    # Create new part with same specs but reset hours
    new_part = MachinePart(
        machine_id=machine_id,
        material_id=old_part.material_id,
        position=old_part.position,
        lifetime_hours=old_part.lifetime_hours,
        current_hours=Decimal("0"),
        lifetime_percentage=Decimal("100"),
        installed_date=date.today(),
        expected_replace_date=old_part.expected_replace_date,
        serial_number=data.new_serial_number,
        lot_number=data.new_lot_number,
        note=data.note,
        status="active",
    )
    db.add(new_part)
    await db.flush()
    await db.refresh(new_part)

    resp = MachinePartResponse.model_validate(new_part)
    if new_part.material:
        resp.material_code = new_part.material.code
        resp.material_name = new_part.material.name
    return resp


# ===================== MAINTENANCE LOGS =====================

async def _generate_log_number(db: AsyncSession) -> str:
    """Generate next maintenance log number: ML-YYMMDD-XXX."""
    today = date.today()
    prefix = f"ML-{today.strftime('%y%m%d')}"
    result = await db.execute(
        select(func.count(MaintenanceLog.id)).where(MaintenanceLog.log_number.like(f"{prefix}%"))
    )
    count = (result.scalar() or 0) + 1
    return f"{prefix}-{count:03d}"


@router.get("/{machine_id}/maintenance", response_model=MaintenanceLogListResponse)
async def list_maintenance_logs(
    machine_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    maintenance_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List maintenance logs for a machine."""
    query = select(MaintenanceLog).where(MaintenanceLog.machine_id == machine_id)
    count_query = select(func.count(MaintenanceLog.id)).where(MaintenanceLog.machine_id == machine_id)

    if maintenance_type:
        query = query.where(MaintenanceLog.maintenance_type == maintenance_type)
        count_query = count_query.where(MaintenanceLog.maintenance_type == maintenance_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(MaintenanceLog.maintenance_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    responses = []
    for log in logs:
        resp = MaintenanceLogResponse.model_validate(log)
        resp.performer_name = log.performer.full_name if log.performer else None
        resp.machine_name = log.machine.name if log.machine else None
        resp.machine_code = log.machine.code if log.machine else None
        # Build items
        resp.items = []
        for item in (log.items or []):
            item_resp = MaintenanceLogItemResponse.model_validate(item)
            if item.material:
                item_resp.material_name = item.material.name
                item_resp.material_code = item.material.code
            resp.items.append(item_resp)
        responses.append(resp)

    return MaintenanceLogListResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{machine_id}/maintenance", response_model=MaintenanceLogResponse, status_code=201)
async def create_maintenance_log(
    machine_id: int,
    data: MaintenanceLogCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a maintenance log entry."""
    machine_result = await db.execute(select(Machine).where(Machine.id == machine_id))
    machine = machine_result.scalar_one_or_none()
    if not machine:
        raise HTTPException(404, "Machine not found")

    log_number = await _generate_log_number(db)

    log = MaintenanceLog(
        log_number=log_number,
        machine_id=machine_id,
        maintenance_type=data.maintenance_type,
        maintenance_date=data.maintenance_date,
        shift=data.shift,
        running_hours_at_time=data.running_hours_at_time or machine.current_running_hours,
        description=data.description,
        root_cause=data.root_cause,
        action_taken=data.action_taken,
        downtime_hours=data.downtime_hours,
        issue_id=data.issue_id,
        performed_by=current_user.id,
        status=data.status,
    )
    db.add(log)
    await db.flush()

    # Add items
    for item_data in data.items:
        item = MaintenanceLogItem(
            log_id=log.id,
            material_id=item_data.material_id,
            old_part_id=item_data.old_part_id,
            quantity=item_data.quantity,
            action_type=item_data.action_type,
            note=item_data.note,
        )
        db.add(item)

    # Update machine last maintenance date
    machine.last_maintenance_date = data.maintenance_date

    await db.flush()
    await db.refresh(log)

    resp = MaintenanceLogResponse.model_validate(log)
    resp.performer_name = current_user.full_name
    resp.machine_name = machine.name
    resp.machine_code = machine.code
    resp.items = []
    for item in (log.items or []):
        item_resp = MaintenanceLogItemResponse.model_validate(item)
        if item.material:
            item_resp.material_name = item.material.name
            item_resp.material_code = item.material.code
        resp.items.append(item_resp)
    return resp


# ===================== RUNNING HOURS =====================

@router.get("/{machine_id}/running-hours", response_model=list[RunningHourResponse])
async def list_running_hours(
    machine_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get running hours records for a machine."""
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(MachineRunningHour)
        .where(
            MachineRunningHour.machine_id == machine_id,
            MachineRunningHour.record_date >= start_date,
        )
        .order_by(MachineRunningHour.record_date.desc())
    )
    records = result.scalars().all()

    responses = []
    for rec in records:
        resp = RunningHourResponse.model_validate(rec)
        resp.recorder_name = rec.recorder.full_name if rec.recorder else None
        responses.append(resp)
    return responses


@router.post("/{machine_id}/running-hours", response_model=RunningHourResponse, status_code=201)
async def record_running_hours(
    machine_id: int,
    data: RunningHourCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Record running hours for a machine."""
    machine_result = await db.execute(select(Machine).where(Machine.id == machine_id))
    machine = machine_result.scalar_one_or_none()
    if not machine:
        raise HTTPException(404, "Machine not found")

    # Calculate new cumulative hours
    new_cumulative = machine.current_running_hours + data.running_hours

    record = MachineRunningHour(
        machine_id=machine_id,
        record_date=data.record_date,
        running_hours=data.running_hours,
        cumulative_hours=new_cumulative,
        shift=data.shift,
        recorded_by=current_user.id,
        note=data.note,
    )
    db.add(record)

    # Update machine total hours
    machine.current_running_hours = new_cumulative

    # Update all active parts on this machine — increment their hours
    parts_result = await db.execute(
        select(MachinePart).where(
            MachinePart.machine_id == machine_id,
            MachinePart.status.in_(["active", "warning", "critical"]),
        )
    )
    for part in parts_result.scalars().all():
        part.current_hours += data.running_hours
        if part.lifetime_hours and part.lifetime_hours > 0:
            remaining = max(Decimal("0"), part.lifetime_hours - part.current_hours)
            part.lifetime_percentage = round((remaining / part.lifetime_hours) * 100, 2)

            if part.lifetime_percentage <= 0:
                part.status = "expired"
            elif part.lifetime_percentage <= 10:
                part.status = "critical"
            elif part.lifetime_percentage <= 30:
                part.status = "warning"
            else:
                part.status = "active"

    await db.flush()
    await db.refresh(record)

    resp = RunningHourResponse.model_validate(record)
    resp.recorder_name = current_user.full_name
    return resp


# ===================== TIMELINE =====================

@router.get("/{machine_id}/timeline")
async def get_machine_timeline(
    machine_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get combined timeline of maintenance and part replacements for a machine."""
    timeline = []

    # Maintenance logs
    logs_result = await db.execute(
        select(MaintenanceLog)
        .where(MaintenanceLog.machine_id == machine_id)
        .order_by(MaintenanceLog.maintenance_date.desc())
        .limit(limit)
    )
    for log in logs_result.scalars().all():
        timeline.append({
            "type": "maintenance",
            "date": log.maintenance_date.isoformat(),
            "log_number": log.log_number,
            "maintenance_type": log.maintenance_type,
            "description": log.description,
            "root_cause": log.root_cause,
            "action_taken": log.action_taken,
            "downtime_hours": float(log.downtime_hours) if log.downtime_hours else None,
            "performer": log.performer.full_name if log.performer else None,
            "status": log.status,
            "items_count": len(log.items or []),
        })

    # Part replacements (replaced parts)
    parts_result = await db.execute(
        select(MachinePart)
        .where(MachinePart.machine_id == machine_id, MachinePart.status == "replaced")
        .order_by(MachinePart.last_replaced_date.desc())
        .limit(limit)
    )
    for part in parts_result.scalars().all():
        timeline.append({
            "type": "part_replacement",
            "date": part.last_replaced_date.isoformat() if part.last_replaced_date else part.installed_date.isoformat() if part.installed_date else None,
            "material_code": part.material.code if part.material else None,
            "material_name": part.material.name if part.material else None,
            "position": part.position,
            "hours_at_replacement": float(part.current_hours),
            "lifetime_hours": float(part.lifetime_hours) if part.lifetime_hours else None,
        })

    # Sort by date descending
    timeline.sort(key=lambda x: x.get("date") or "", reverse=True)
    return timeline[:limit]
