"""Issues (Phiếu xuất kho) API endpoints."""

from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.issue import Issue, IssueItem
from app.models.inventory import Inventory, InventoryTransaction
from app.models.material import Material
from app.schemas.issue import (
    IssueCreate, IssueUpdate, IssueResponse, IssueListResponse,
)
from app.core.permissions import require_permission, Permission
from app.core.security import get_current_active_user

router = APIRouter()


async def _generate_issue_number(db: AsyncSession) -> str:
    """Generate next issue number: XK-YYMMDD-XXX."""
    today = date.today()
    prefix = f"XK-{today.strftime('%y%m%d')}"
    result = await db.execute(
        select(func.count(Issue.id)).where(Issue.issue_number.like(f"{prefix}%"))
    )
    count = (result.scalar() or 0) + 1
    return f"{prefix}-{count:03d}"


@router.get("", response_model=IssueListResponse)
async def list_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    issue_type: str | None = None,
    machine: str | None = None,
    line: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List issue documents with filters."""
    query = select(Issue)
    count_query = select(func.count(Issue.id))

    if status:
        query = query.where(Issue.status == status)
        count_query = count_query.where(Issue.status == status)
    if issue_type:
        query = query.where(Issue.issue_type == issue_type)
        count_query = count_query.where(Issue.issue_type == issue_type)
    if machine:
        query = query.where(Issue.machine.ilike(f"%{machine}%"))
        count_query = count_query.where(Issue.machine.ilike(f"%{machine}%"))
    if line:
        query = query.where(Issue.line == line)
        count_query = count_query.where(Issue.line == line)
    if date_from:
        query = query.where(Issue.issue_date >= date_from)
        count_query = count_query.where(Issue.issue_date >= date_from)
    if date_to:
        query = query.where(Issue.issue_date <= date_to)
        count_query = count_query.where(Issue.issue_date <= date_to)
    if search:
        search_filter = (
            (Issue.issue_number.ilike(f"%{search}%"))
            | (Issue.work_order.ilike(f"%{search}%"))
            | (Issue.receiver.ilike(f"%{search}%"))
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Issue.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    issues = result.scalars().all()

    return IssueListResponse(
        items=[IssueResponse.model_validate(i) for i in issues],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=IssueResponse, status_code=201)
async def create_issue(
    data: IssueCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new issue document."""
    issue_number = await _generate_issue_number(db)

    # Calculate total using material prices
    total = Decimal("0")
    for item_data in data.items:
        mat_result = await db.execute(select(Material).where(Material.id == item_data.material_id))
        material = mat_result.scalar_one_or_none()
        if material and material.price:
            total += item_data.quantity * material.price

    issue = Issue(
        issue_number=issue_number,
        issue_date=data.issue_date,
        issue_type=data.issue_type,
        machine=data.machine,
        line=data.line,
        shift=data.shift,
        receiver=data.receiver,
        department=data.department,
        reason=data.reason,
        work_order=data.work_order,
        remark=data.remark,
        status="draft",
        total_amount=total,
        created_by=current_user.id,
    )
    db.add(issue)
    await db.flush()

    # Add items
    for item_data in data.items:
        mat_result = await db.execute(select(Material).where(Material.id == item_data.material_id))
        material = mat_result.scalar_one_or_none()
        unit_price = material.price if material else None
        item_total = item_data.quantity * unit_price if unit_price else None

        item = IssueItem(
            issue_id=issue.id,
            material_id=item_data.material_id,
            location_id=item_data.location_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=item_total,
            lot_number=item_data.lot_number,
            serial_number=item_data.serial_number,
            note=item_data.note,
        )
        db.add(item)

    await db.flush()
    await db.refresh(issue)
    return IssueResponse.model_validate(issue)


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific issue document."""
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return IssueResponse.model_validate(issue)


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int,
    data: IssueUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft issue."""
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.status != "draft":
        raise HTTPException(status_code=400, detail="Can only edit draft issues")

    update_data = data.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in update_data.items():
        setattr(issue, field, value)

    if data.items is not None:
        for item in issue.items:
            await db.delete(item)
        total = Decimal("0")
        for item_data in data.items:
            mat_result = await db.execute(select(Material).where(Material.id == item_data.material_id))
            material = mat_result.scalar_one_or_none()
            unit_price = material.price if material else None
            item_total = item_data.quantity * unit_price if unit_price else None
            if item_total:
                total += item_total
            item = IssueItem(
                issue_id=issue.id,
                material_id=item_data.material_id,
                location_id=item_data.location_id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                total_price=item_total,
                lot_number=item_data.lot_number,
                serial_number=item_data.serial_number,
                note=item_data.note,
            )
            db.add(item)
        issue.total_amount = total

    await db.flush()
    await db.refresh(issue)
    return IssueResponse.model_validate(issue)


@router.post("/{issue_id}/approve", response_model=IssueResponse)
async def approve_issue(
    issue_id: int,
    current_user: User = Depends(require_permission(Permission.APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Approve an issue and deduct inventory."""
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.status != "draft":
        raise HTTPException(status_code=400, detail=f"Issue is already '{issue.status}'")

    # Deduct inventory for each item
    for item in issue.items:
        inv_result = await db.execute(
            select(Inventory).where(
                Inventory.material_id == item.material_id,
                Inventory.location_id == item.location_id,
            )
        )
        inv = inv_result.scalar_one_or_none()

        if not inv or inv.quantity < item.quantity:
            mat = await db.execute(select(Material).where(Material.id == item.material_id))
            material = mat.scalar_one_or_none()
            mat_name = material.name if material else f"ID:{item.material_id}"
            available = inv.quantity if inv else 0
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{mat_name}': available={available}, requested={item.quantity}",
            )

        inv.quantity -= item.quantity

        # Log transaction
        transaction = InventoryTransaction(
            inventory_id=inv.id,
            transaction_type="issue_out",
            quantity=-item.quantity,
            balance_after=inv.quantity,
            reference_type="issue",
            reference_id=issue.id,
            note=f"Issue {issue.issue_number}",
            user_id=current_user.id,
        )
        db.add(transaction)

    # Update issue status
    issue.status = "approved"
    issue.approved_by = current_user.id
    issue.approved_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(issue)
    return IssueResponse.model_validate(issue)


@router.post("/{issue_id}/cancel", response_model=IssueResponse)
async def cancel_issue(
    issue_id: int,
    current_user: User = Depends(require_permission(Permission.APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an issue."""
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.status == "cancelled":
        raise HTTPException(status_code=400, detail="Issue is already cancelled")

    issue.status = "cancelled"
    await db.flush()
    await db.refresh(issue)
    return IssueResponse.model_validate(issue)
