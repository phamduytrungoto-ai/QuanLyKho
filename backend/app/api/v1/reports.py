from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
import io

from app.database import get_db
from app.models.material import Material, Unit
from app.models.inventory import Inventory, InventoryTransaction
from app.models.machine import MaintenanceLog, MaintenanceLogItem, Machine, ProductionLine
from app.schemas.report import (
    InventoryValuationReport, InventoryValuationItem,
    StockCardReport, StockCardItem,
    AbcAnalysisReport, AbcAnalysisItem,
    MaintenanceCostReport, MaintenanceCostItem
)

router = APIRouter()

def create_excel_response(headers: list, rows: list, filename: str):
    from openpyxl import Workbook
    from fastapi.responses import StreamingResponse
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"}
    )

@router.get("/inventory-valuation", response_model=None)
async def get_inventory_valuation(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    warehouse_id: Optional[int] = None,
    export: bool = False,
    db: AsyncSession = Depends(get_db)
):
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date.replace(day=1) # Default to start of month

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    # Build subquery for transactions
    t = InventoryTransaction
    i = Inventory
    
    # We group by material_id
    # To do this correctly: Join Transaction -> Inventory -> Material
    stmt = select(
        Material.id.label("material_id"),
        Material.code.label("material_code"),
        Material.name.label("material_name"),
        Unit.name.label("unit"),
        func.coalesce(Material.price, 0).label("price"),
        func.sum(case((t.created_at < start_dt, t.quantity), else_=0)).label("opening_stock"),
        func.sum(case((and_(t.created_at >= start_dt, t.created_at <= end_dt, t.quantity > 0), t.quantity), else_=0)).label("inward_qty"),
        func.sum(case((and_(t.created_at >= start_dt, t.created_at <= end_dt, t.quantity < 0), func.abs(t.quantity)), else_=0)).label("outward_qty"),
    ).select_from(Material).outerjoin(i, i.material_id == Material.id)\
     .outerjoin(t, t.inventory_id == i.id)\
     .outerjoin(Unit, Unit.id == Material.unit_id)

    if warehouse_id:
        stmt = stmt.filter(i.location_id == warehouse_id) # Simplify location as warehouse for now

    stmt = stmt.group_by(Material.id, Material.code, Material.name, Unit.name, Material.price)
    
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    tot_open = tot_in = tot_out = tot_close = 0
    
    for r in rows:
        price = r.price or 0
        open_stk = r.opening_stock or 0
        in_qty = r.inward_qty or 0
        out_qty = r.outward_qty or 0
        close_stk = open_stk + in_qty - out_qty
        
        item = InventoryValuationItem(
            material_id=r.material_id,
            material_code=r.material_code,
            material_name=r.material_name,
            unit=r.unit or "Cái",
            opening_stock=open_stk,
            opening_value=open_stk * price,
            inward_qty=in_qty,
            inward_value=in_qty * price,
            outward_qty=out_qty,
            outward_value=out_qty * price,
            closing_stock=close_stk,
            closing_value=close_stk * price
        )
        if open_stk != 0 or in_qty != 0 or out_qty != 0 or close_stk != 0:
            items.append(item)
            tot_open += item.opening_value
            tot_in += item.inward_value
            tot_out += item.outward_value
            tot_close += item.closing_value

    if export:
        headers = ["Mã VT", "Tên VT", "ĐVT", "Tồn đầu", "GT Tồn đầu", "Nhập", "GT Nhập", "Xuất", "GT Xuất", "Tồn cuối", "GT Tồn cuối"]
        excel_rows = [
            [i.material_code, i.material_name, i.unit, i.opening_stock, i.opening_value, i.inward_qty, i.inward_value, i.outward_qty, i.outward_value, i.closing_stock, i.closing_value]
            for i in items
        ]
        return create_excel_response(headers, excel_rows, "Bao_Cao_NXT")

    return InventoryValuationReport(
        start_date=start_date, end_date=end_date, warehouse_id=warehouse_id,
        items=items,
        total_opening_value=tot_open, total_inward_value=tot_in,
        total_outward_value=tot_out, total_closing_value=tot_close
    )

@router.get("/stock-card", response_model=None)
async def get_stock_card(
    material_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    export: bool = False,
    db: AsyncSession = Depends(get_db)
):
    mat_stmt = select(Material, Unit).outerjoin(Unit, Unit.id == Material.unit_id).where(Material.id == material_id)
    mat_res = await db.execute(mat_stmt)
    mat_row = mat_res.first()
    if not mat_row:
        raise HTTPException(404, "Material not found")
    mat, unit = mat_row

    if not end_date: end_date = date.today()
    if not start_date: start_date = end_date.replace(day=1)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    # Get opening balance
    open_stmt = select(func.sum(InventoryTransaction.quantity)).select_from(InventoryTransaction)\
        .join(Inventory, Inventory.id == InventoryTransaction.inventory_id)\
        .where(Inventory.material_id == material_id, InventoryTransaction.created_at < start_dt)
    open_res = await db.execute(open_stmt)
    opening_balance = open_res.scalar() or 0

    # Get transactions
    tx_stmt = select(InventoryTransaction).join(Inventory)\
        .where(
            Inventory.material_id == material_id,
            InventoryTransaction.created_at >= start_dt,
            InventoryTransaction.created_at <= end_dt
        ).order_by(InventoryTransaction.created_at.asc())
    tx_res = await db.execute(tx_stmt)
    transactions = tx_res.scalars().all()

    items = []
    current_bal = opening_balance
    for tx in transactions:
        in_q = tx.quantity if tx.quantity > 0 else 0
        out_q = abs(tx.quantity) if tx.quantity < 0 else 0
        current_bal += tx.quantity
        items.append(StockCardItem(
            transaction_date=tx.created_at.date(),
            transaction_type=tx.transaction_type,
            reference_number=f"{tx.reference_type}-{tx.reference_id}" if tx.reference_id else None,
            inward_qty=in_q,
            outward_qty=out_q,
            balance=current_bal,
            note=tx.note
        ))

    if export:
        headers = ["Ngày", "Loại GD", "Mã tham chiếu", "SL Nhập", "SL Xuất", "Tồn", "Ghi chú"]
        excel_rows = [[i.transaction_date.strftime("%Y-%m-%d"), i.transaction_type, i.reference_number, i.inward_qty, i.outward_qty, i.balance, i.note] for i in items]
        return create_excel_response(headers, excel_rows, f"The_Kho_{mat.code}")

    return StockCardReport(
        material_id=mat.id, material_code=mat.code, material_name=mat.name, unit=unit.name if unit else "Cái",
        start_date=start_date, end_date=end_date, opening_balance=opening_balance, closing_balance=current_bal,
        transactions=items
    )

@router.get("/abc-analysis", response_model=None)
async def get_abc_analysis(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    export: bool = False,
    db: AsyncSession = Depends(get_db)
):
    if not end_date: end_date = date.today()
    if not start_date: start_date = end_date - timedelta(days=90)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    t = InventoryTransaction
    i = Inventory
    # Find total outbound value
    stmt = select(
        Material.id, Material.code, Material.name, Unit.name.label('unit'),
        func.sum(func.abs(t.quantity)).label("usage_qty"),
        (func.sum(func.abs(t.quantity)) * func.coalesce(Material.price, 0)).label("usage_value")
    ).select_from(Material)\
     .outerjoin(Unit, Unit.id == Material.unit_id)\
     .join(i, i.material_id == Material.id)\
     .join(t, t.inventory_id == i.id)\
     .where(t.quantity < 0, t.created_at >= start_dt, t.created_at <= end_dt)\
     .group_by(Material.id, Material.code, Material.name, Unit.name, Material.price)
    
    res = await db.execute(stmt)
    rows = res.all()

    # Sort descending by value
    rows_sorted = sorted(rows, key=lambda x: x.usage_value, reverse=True)
    total_val = sum(r.usage_value for r in rows_sorted)

    items = []
    cum_val = 0
    sa = sb = sc = 0

    for r in rows_sorted:
        cum_val += r.usage_value
        pct = (cum_val / total_val * 100) if total_val > 0 else 0
        
        if pct <= 70:
            cls = 'A'
            sa += 1
        elif pct <= 90:
            cls = 'B'
            sb += 1
        else:
            cls = 'C'
            sc += 1

        items.append(AbcAnalysisItem(
            material_id=r.id, material_code=r.code, material_name=r.name, unit=r.unit or "Cái",
            total_usage_qty=r.usage_qty, total_usage_value=r.usage_value,
            cumulative_value=cum_val, cumulative_percentage=pct, abc_class=cls
        ))

    if export:
        headers = ["Mã VT", "Tên VT", "ĐVT", "SL Xuất", "GT Xuất", "GT Luỹ kế", "% Luỹ kế", "Phân nhóm ABC"]
        excel_rows = [[i.material_code, i.material_name, i.unit, i.total_usage_qty, i.total_usage_value, i.cumulative_value, float(i.cumulative_percentage), i.abc_class] for i in items]
        return create_excel_response(headers, excel_rows, "Phan_Tich_ABC")

    return AbcAnalysisReport(start_date=start_date, end_date=end_date, items=items, summary_a=sa, summary_b=sb, summary_c=sc)

@router.get("/maintenance-cost", response_model=None)
async def get_maintenance_cost(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    export: bool = False,
    db: AsyncSession = Depends(get_db)
):
    if not end_date: end_date = date.today()
    if not start_date: start_date = end_date.replace(day=1)
    
    # query machines with their maintenance logs inside date range
    stmt = select(
        Machine.id, Machine.code, Machine.name, ProductionLine.name.label('line_name'),
        func.count(MaintenanceLog.id).label("m_count"),
        func.sum(MaintenanceLog.downtime_hours).label("downtime")
    ).select_from(Machine).outerjoin(ProductionLine, ProductionLine.id == Machine.line_id)\
     .outerjoin(MaintenanceLog, and_(
         MaintenanceLog.machine_id == Machine.id,
         func.date(MaintenanceLog.maintenance_date) >= start_date,
         func.date(MaintenanceLog.maintenance_date) <= end_date
     )).group_by(Machine.id, Machine.code, Machine.name, ProductionLine.name)

    res = await db.execute(stmt)
    machines = res.all()

    items = []
    tot_overall = 0
    for m in machines:
        if m.m_count == 0: continue
        # Find parts replaced and costs for this machine
        cost_stmt = select(func.sum(MaintenanceLogItem.quantity), func.sum(MaintenanceLogItem.quantity * func.coalesce(Material.price, 0)))\
            .select_from(MaintenanceLogItem)\
            .join(MaintenanceLog, MaintenanceLog.id == MaintenanceLogItem.log_id)\
            .join(Material, Material.id == MaintenanceLogItem.material_id)\
            .where(
                MaintenanceLog.machine_id == m.id,
                func.date(MaintenanceLog.maintenance_date) >= start_date,
                func.date(MaintenanceLog.maintenance_date) <= end_date
            )
        c_res = await db.execute(cost_stmt)
        c_row = c_res.first()
        p_count = c_row[0] or 0
        p_cost = c_row[1] or 0

        items.append(MaintenanceCostItem(
            machine_id=m.id, machine_code=m.code, machine_name=m.name, line_name=m.line_name,
            maintenance_count=m.m_count, total_downtime=m.downtime or 0,
            parts_replaced_count=p_count, total_cost=p_cost
        ))
        tot_overall += p_cost

    if export:
        headers = ["Mã máy", "Tên máy", "Line", "Số lần bảo trì", "Downtime (h)", "SL vật tư thay thế", "Tổng chi phí"]
        excel_rows = [[i.machine_code, i.machine_name, i.line_name, i.maintenance_count, i.total_downtime, i.parts_replaced_count, i.total_cost] for i in items]
        return create_excel_response(headers, excel_rows, "Chi_Phi_Bao_Tri")

    return MaintenanceCostReport(start_date=start_date, end_date=end_date, items=items, total_overall_cost=tot_overall)
