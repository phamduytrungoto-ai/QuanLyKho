"""Receipts (Phiếu nhập kho) API endpoints."""

from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.receipt import Receipt, ReceiptItem
from app.models.inventory import Inventory, InventoryTransaction
from app.models.material import Material
from app.schemas.receipt import (
    ReceiptCreate, ReceiptUpdate, ReceiptResponse, ReceiptListResponse,
)
from app.core.permissions import require_permission, Permission
from app.core.security import get_current_active_user

router = APIRouter()


async def _generate_receipt_number(db: AsyncSession) -> str:
    """Generate next receipt number: NK-YYMMDD-XXX."""
    today = date.today()
    prefix = f"NK-{today.strftime('%y%m%d')}"
    result = await db.execute(
        select(func.count(Receipt.id)).where(Receipt.receipt_number.like(f"{prefix}%"))
    )
    count = (result.scalar() or 0) + 1
    return f"{prefix}-{count:03d}"


@router.get("", response_model=ReceiptListResponse)
async def list_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    receipt_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List receipt documents with filters."""
    query = select(Receipt)
    count_query = select(func.count(Receipt.id))

    if status:
        query = query.where(Receipt.status == status)
        count_query = count_query.where(Receipt.status == status)
    if receipt_type:
        query = query.where(Receipt.receipt_type == receipt_type)
        count_query = count_query.where(Receipt.receipt_type == receipt_type)
    if date_from:
        query = query.where(Receipt.receipt_date >= date_from)
        count_query = count_query.where(Receipt.receipt_date >= date_from)
    if date_to:
        query = query.where(Receipt.receipt_date <= date_to)
        count_query = count_query.where(Receipt.receipt_date <= date_to)
    if search:
        search_filter = (
            (Receipt.receipt_number.ilike(f"%{search}%"))
            | (Receipt.po_number.ilike(f"%{search}%"))
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Receipt.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    receipts = result.scalars().all()

    return ReceiptListResponse(
        items=[ReceiptResponse.model_validate(r) for r in receipts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ReceiptResponse, status_code=201)
async def create_receipt(
    data: ReceiptCreate,
    current_user: User = Depends(require_permission(Permission.CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new receipt document."""
    receipt_number = await _generate_receipt_number(db)

    # Calculate total
    total = Decimal("0")
    for item in data.items:
        if item.unit_price:
            total += item.quantity * item.unit_price

    receipt = Receipt(
        receipt_number=receipt_number,
        receipt_date=data.receipt_date,
        receipt_type=data.receipt_type,
        supplier_id=data.supplier_id,
        po_number=data.po_number,
        invoice_number=data.invoice_number,
        note=data.note,
        status="draft",
        total_amount=total,
        created_by=current_user.id,
    )
    db.add(receipt)
    await db.flush()

    # Add items
    for item_data in data.items:
        item_total = None
        if item_data.unit_price:
            item_total = item_data.quantity * item_data.unit_price
        item = ReceiptItem(
            receipt_id=receipt.id,
            material_id=item_data.material_id,
            location_id=item_data.location_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_total,
            lot_number=item_data.lot_number,
            serial_number=item_data.serial_number,
            expiry_date=item_data.expiry_date,
            note=item_data.note,
        )
        db.add(item)

    await db.flush()
    await db.refresh(receipt)
    return ReceiptResponse.model_validate(receipt)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific receipt document."""
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptResponse.model_validate(receipt)


@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: int,
    data: ReceiptUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft receipt."""
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if receipt.status != "draft":
        raise HTTPException(status_code=400, detail="Can only edit draft receipts")

    update_data = data.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in update_data.items():
        setattr(receipt, field, value)

    # Update items if provided
    if data.items is not None:
        # Delete existing items
        for item in receipt.items:
            await db.delete(item)
        # Add new items
        total = Decimal("0")
        for item_data in data.items:
            item_total = None
            if item_data.unit_price:
                item_total = item_data.quantity * item_data.unit_price
                total += item_total
            item = ReceiptItem(
                receipt_id=receipt.id,
                material_id=item_data.material_id,
                location_id=item_data.location_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_total,
                lot_number=item_data.lot_number,
                serial_number=item_data.serial_number,
                expiry_date=item_data.expiry_date,
                note=item_data.note,
            )
            db.add(item)
        receipt.total_amount = total

    await db.flush()
    await db.refresh(receipt)
    return ReceiptResponse.model_validate(receipt)


@router.post("/{receipt_id}/approve", response_model=ReceiptResponse)
async def approve_receipt(
    receipt_id: int,
    current_user: User = Depends(require_permission(Permission.APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Approve a receipt and update inventory."""
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if receipt.status != "draft":
        raise HTTPException(status_code=400, detail=f"Receipt is already '{receipt.status}'")

    # Update inventory for each item
    for item in receipt.items:
        # Find or create inventory record
        inv_result = await db.execute(
            select(Inventory).where(
                Inventory.material_id == item.material_id,
                Inventory.location_id == item.location_id,
            )
        )
        inv = inv_result.scalar_one_or_none()

        if inv:
            inv.quantity += item.quantity
        else:
            inv = Inventory(
                material_id=item.material_id,
                location_id=item.location_id,
                quantity=item.quantity,
            )
            db.add(inv)
            await db.flush()

        # Log transaction
        transaction = InventoryTransaction(
            inventory_id=inv.id,
            transaction_type="receipt_in",
            quantity=item.quantity,
            balance_after=inv.quantity,
            reference_type="receipt",
            reference_id=receipt.id,
            note=f"Receipt {receipt.receipt_number}",
            user_id=current_user.id,
        )
        db.add(transaction)

    # Update receipt status
    receipt.status = "approved"
    receipt.approved_by = current_user.id
    receipt.approved_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(receipt)
    return ReceiptResponse.model_validate(receipt)


@router.post("/{receipt_id}/cancel", response_model=ReceiptResponse)
async def cancel_receipt(
    receipt_id: int,
    current_user: User = Depends(require_permission(Permission.APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a receipt."""
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if receipt.status == "cancelled":
        raise HTTPException(status_code=400, detail="Receipt is already cancelled")

    receipt.status = "cancelled"
    await db.flush()
    await db.refresh(receipt)
    return ReceiptResponse.model_validate(receipt)
