"""Database seeding script with demo data."""

import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.database import engine, async_session_factory, Base
from app.models import *
from app.core.security import get_password_hash


async def seed_database():
    """Create tables and seed with demo data."""

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")

    async with async_session_factory() as session:
        # Check if already seeded
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("⚠️  Database already seeded, skipping...")
            return

        # ============== Users ==============
        users = [
            User(username="admin", email="admin@factory.local", full_name="Administrator",
                 password_hash=get_password_hash("admin123"), role="admin", department="IT"),
            User(username="warehouse", email="wh@factory.local", full_name="Nguyễn Văn Kho",
                 password_hash=get_password_hash("wh123"), role="warehouse", department="Warehouse"),
            User(username="production", email="prod@factory.local", full_name="Trần Thị Sản Xuất",
                 password_hash=get_password_hash("prod123"), role="production", department="Production"),
            User(username="maintenance", email="maint@factory.local", full_name="Lê Văn Bảo Trì",
                 password_hash=get_password_hash("maint123"), role="maintenance", department="Maintenance"),
            User(username="engineering", email="eng@factory.local", full_name="Phạm Kỹ Sư",
                 password_hash=get_password_hash("eng123"), role="engineering", department="Engineering"),
            User(username="purchasing", email="pur@factory.local", full_name="Hoàng Mua Hàng",
                 password_hash=get_password_hash("pur123"), role="purchasing", department="Purchasing"),
            User(username="qa", email="qa@factory.local", full_name="Vũ Chất Lượng",
                 password_hash=get_password_hash("qa123"), role="qa", department="QA"),
            User(username="manager", email="mgr@factory.local", full_name="Đỗ Quản Lý",
                 password_hash=get_password_hash("mgr123"), role="manager", department="Management"),
            User(username="director", email="dir@factory.local", full_name="Ngô Giám Đốc",
                 password_hash=get_password_hash("dir123"), role="director", department="Board"),
        ]
        session.add_all(users)
        await session.flush()
        print("✅ Users seeded (9 users)")

        # ============== Units ==============
        units = [
            Unit(code="PCS", name="Cái", name_en="Pieces", name_ja="個"),
            Unit(code="ROLL", name="Cuộn", name_en="Roll", name_ja="ロール"),
            Unit(code="KG", name="Kg", name_en="Kilogram", name_ja="キロ"),
            Unit(code="L", name="Lít", name_en="Liter", name_ja="リットル"),
            Unit(code="M", name="Mét", name_en="Meter", name_ja="メートル"),
            Unit(code="BOX", name="Hộp", name_en="Box", name_ja="箱"),
            Unit(code="SET", name="Bộ", name_en="Set", name_ja="セット"),
            Unit(code="BTL", name="Chai", name_en="Bottle", name_ja="本"),
        ]
        session.add_all(units)
        await session.flush()
        print("✅ Units seeded (8 units)")

        # ============== Categories ==============
        categories = [
            MaterialCategory(code="SP", name="Linh kiện sửa chữa", name_en="Spare Parts", name_ja="スペアパーツ"),
            MaterialCategory(code="CS", name="Vật tư tiêu hao", name_en="Consumables", name_ja="消耗品"),
            MaterialCategory(code="TL", name="Dụng cụ", name_en="Tools", name_ja="工具"),
            MaterialCategory(code="CH", name="Hóa chất", name_en="Chemicals", name_ja="化学品"),
            MaterialCategory(code="EL", name="Linh kiện điện", name_en="Electrical", name_ja="電気部品"),
            MaterialCategory(code="MC", name="Linh kiện cơ khí", name_en="Mechanical", name_ja="機械部品"),
        ]
        session.add_all(categories)
        await session.flush()
        print("✅ Categories seeded (6 categories)")

        # ============== Suppliers ==============
        suppliers = [
            Supplier(code="SUP001", name="Panasonic Vietnam", name_en="Panasonic Vietnam",
                     contact_person="Mr. Tanaka", phone="028-1234-5678", email="order@panasonic.vn",
                     address="KCN Biên Hòa, Đồng Nai", lead_time_days=30, payment_terms="Net 30"),
            Supplier(code="SUP002", name="Mitsubishi Electric", name_en="Mitsubishi Electric",
                     contact_person="Ms. Yamada", phone="028-2345-6789", email="sales@mitsubishi.vn",
                     address="KCN Thăng Long, Hà Nội", lead_time_days=45, payment_terms="Net 45"),
            Supplier(code="SUP003", name="Keyence Vietnam", name_en="Keyence Vietnam",
                     contact_person="Mr. Suzuki", phone="028-3456-7890", email="info@keyence.vn",
                     address="Quận 7, TP.HCM", lead_time_days=60, payment_terms="Net 30"),
            Supplier(code="SUP004", name="Omron Vietnam", name_en="Omron Vietnam",
                     contact_person="Ms. Saito", phone="028-4567-8901", email="support@omron.vn",
                     address="KCN Amata, Đồng Nai", lead_time_days=30, payment_terms="Net 30"),
            Supplier(code="SUP005", name="Henkel Vietnam", name_en="Henkel Vietnam",
                     contact_person="Mr. Nguyễn Văn A", phone="028-5678-9012", email="sales@henkel.vn",
                     address="Bình Dương", lead_time_days=14, payment_terms="Net 15"),
        ]
        session.add_all(suppliers)
        await session.flush()
        print("✅ Suppliers seeded (5 suppliers)")

        # ============== Warehouses ==============
        wh_main = Warehouse(code="WH01", name="Kho linh kiện", name_en="Spare Parts Warehouse",
                           warehouse_type="spare_part", manager="Nguyễn Văn Kho")
        wh_chem = Warehouse(code="WH02", name="Kho hóa chất", name_en="Chemical Warehouse",
                           warehouse_type="chemical", manager="Nguyễn Văn Kho")
        wh_cons = Warehouse(code="WH03", name="Kho vật tư tiêu hao", name_en="Consumables Warehouse",
                           warehouse_type="main", manager="Nguyễn Văn Kho")
        wh_insp = Warehouse(code="WH04", name="Kho chờ kiểm tra", name_en="Inspection Warehouse",
                           warehouse_type="inspection")
        wh_defect = Warehouse(code="WH05", name="Kho hàng lỗi", name_en="Defective Warehouse",
                             warehouse_type="defective")
        session.add_all([wh_main, wh_chem, wh_cons, wh_insp, wh_defect])
        await session.flush()
        print("✅ Warehouses seeded (5 warehouses)")

        # ============== Locations ==============
        locations = []
        for rack in ["A", "B", "C", "D"]:
            for level in ["1", "2", "3"]:
                for bin_num in ["01", "02", "03", "04", "05"]:
                    code = f"WH01-{rack}-{level}-{bin_num}"
                    loc = Location(
                        warehouse_id=wh_main.id, code=code,
                        rack=rack, level=level, bin=bin_num,
                        full_path=f"Kho linh kiện > Kệ {rack} > Tầng {level} > Ô {bin_num}",
                    )
                    locations.append(loc)
        # Chemical warehouse locations
        for rack in ["A", "B"]:
            for level in ["1", "2"]:
                for bin_num in ["01", "02", "03"]:
                    code = f"WH02-{rack}-{level}-{bin_num}"
                    loc = Location(
                        warehouse_id=wh_chem.id, code=code,
                        rack=rack, level=level, bin=bin_num,
                        full_path=f"Kho hóa chất > Kệ {rack} > Tầng {level} > Ô {bin_num}",
                    )
                    locations.append(loc)
        # Consumables warehouse
        for rack in ["A", "B", "C"]:
            for level in ["1", "2"]:
                for bin_num in ["01", "02", "03", "04"]:
                    code = f"WH03-{rack}-{level}-{bin_num}"
                    loc = Location(
                        warehouse_id=wh_cons.id, code=code,
                        rack=rack, level=level, bin=bin_num,
                        full_path=f"Kho vật tư > Kệ {rack} > Tầng {level} > Ô {bin_num}",
                    )
                    locations.append(loc)

        session.add_all(locations)
        await session.flush()
        print(f"✅ Locations seeded ({len(locations)} locations)")

        # ============== Materials ==============
        # Get unit/category/supplier IDs
        pcs_unit = units[0]    # PCS
        roll_unit = units[1]   # ROLL
        kg_unit = units[2]     # KG
        l_unit = units[3]      # L
        box_unit = units[5]    # BOX

        sp_cat = categories[0]  # Spare Parts
        cs_cat = categories[1]  # Consumables
        ch_cat = categories[3]  # Chemicals

        materials_data = [
            # Spare Parts
            Material(code="SP0001", name="Sensor Panasonic HG-C1030", name_en="Sensor Panasonic HG-C1030",
                     name_ja="センサー パナソニック HG-C1030", barcode="4549077893215",
                     model="HG-C1030", manufacturer="Panasonic", supplier_id=suppliers[0].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("15000000"), lifetime_hours=8000, lead_time_days=30, moq=1,
                     specifications={"range": "30mm", "output": "Analog", "voltage": "24VDC"}),
            Material(code="SP0002", name="Servo Driver Mitsubishi MR-J4-70A", name_en="Servo Driver Mitsubishi",
                     name_ja="サーボドライバー 三菱 MR-J4-70A", barcode="4902901234567",
                     model="MR-J4-70A", manufacturer="Mitsubishi", supplier_id=suppliers[1].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("25000000"), lifetime_hours=20000, lead_time_days=45, moq=1,
                     specifications={"power": "750W", "voltage": "200V", "protocol": "SSCNET III/H"}),
            Material(code="SP0003", name="Camera Keyence CV-X422A", name_en="Camera Keyence CV-X422A",
                     name_ja="カメラ キーエンス CV-X422A", barcode="4960999876543",
                     model="CV-X422A", manufacturer="Keyence", supplier_id=suppliers[2].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("45000000"), lifetime_hours=15000, lead_time_days=60, moq=1,
                     specifications={"resolution": "2MP", "fps": "120", "interface": "GigE"}),
            Material(code="SP0004", name="PLC Omron NX1P2-1040DT", name_en="PLC Omron NX1P2",
                     name_ja="PLC オムロン NX1P2-1040DT", barcode="4547648123456",
                     model="NX1P2-1040DT", manufacturer="Omron", supplier_id=suppliers[3].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("18000000"), lifetime_hours=30000, lead_time_days=30, moq=1),
            Material(code="SP0005", name="Motor Servo Mitsubishi HG-KR23BK", name_en="Servo Motor Mitsubishi",
                     name_ja="サーボモーター 三菱", barcode="4902901234568",
                     model="HG-KR23BK", manufacturer="Mitsubishi", supplier_id=suppliers[1].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("12000000"), lifetime_hours=20000, lead_time_days=45, moq=1),
            Material(code="SP0006", name="Belt timing 3GT 150mm", name_en="Timing Belt 3GT",
                     name_ja="タイミングベルト", barcode="SP0006BAR",
                     model="3GT-150", manufacturer="Misumi", supplier_id=suppliers[1].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("350000"), lifetime_hours=5000, lead_time_days=14, moq=5),
            Material(code="SP0007", name="Bearing NSK 6204", name_en="Bearing NSK 6204",
                     name_ja="ベアリング NSK 6204", barcode="SP0007BAR",
                     model="6204", manufacturer="NSK", supplier_id=suppliers[1].id,
                     category_id=sp_cat.id, unit_id=pcs_unit.id, material_type="spare_part",
                     price=Decimal("85000"), lifetime_hours=10000, lead_time_days=7, moq=10),
            # Consumables
            Material(code="MT0001", name="Keo UV Henkel Loctite 3491", name_en="UV Adhesive Loctite 3491",
                     name_ja="UV接着剤 ロクタイト 3491", barcode="MT0001BAR",
                     model="Loctite 3491", manufacturer="Henkel", supplier_id=suppliers[4].id,
                     category_id=cs_cat.id, unit_id=kg_unit.id, material_type="consumable",
                     price=Decimal("2500000"), lead_time_days=14, moq=5,
                     consumption_rate=Decimal("0.15"), consumption_unit="g/pcs"),
            Material(code="MT0002", name="Băng keo Nitto 360A 19mm", name_en="Tape Nitto 360A",
                     name_ja="テープ ニットー 360A", barcode="MT0002BAR",
                     model="360A", manufacturer="Nitto Denko", supplier_id=suppliers[4].id,
                     category_id=cs_cat.id, unit_id=roll_unit.id, material_type="consumable",
                     price=Decimal("180000"), lead_time_days=7, moq=20,
                     consumption_rate=Decimal("0.5"), consumption_unit="m/pcs"),
            Material(code="MT0003", name="Khăn lau phòng sạch 9x9", name_en="Cleanroom Wiper 9x9",
                     name_ja="クリーンルームワイパー", barcode="MT0003BAR",
                     model="9x9 Polyester", manufacturer="Berkshire", supplier_id=suppliers[4].id,
                     category_id=cs_cat.id, unit_id=box_unit.id, material_type="consumable",
                     price=Decimal("450000"), lead_time_days=7, moq=10),
            Material(code="MT0004", name="IPA - Isopropyl Alcohol 99%", name_en="IPA 99%",
                     name_ja="IPA イソプロピルアルコール", barcode="MT0004BAR",
                     model="IPA 99%", manufacturer="KMG", supplier_id=suppliers[4].id,
                     category_id=ch_cat.id, unit_id=l_unit.id, material_type="consumable",
                     price=Decimal("120000"), lead_time_days=14, moq=20,
                     consumption_rate=Decimal("0.02"), consumption_unit="ml/pcs"),
            Material(code="MT0005", name="Mỡ bôi trơn NSK LR3", name_en="Grease NSK LR3",
                     name_ja="グリス NSK LR3", barcode="MT0005BAR",
                     model="LR3", manufacturer="NSK", supplier_id=suppliers[1].id,
                     category_id=ch_cat.id, unit_id=kg_unit.id, material_type="consumable",
                     price=Decimal("850000"), lead_time_days=14, moq=5),
            Material(code="MT0006", name="Găng tay phòng sạch size M", name_en="Cleanroom Gloves M",
                     name_ja="クリーンルーム手袋 M", barcode="MT0006BAR",
                     model="Nitrile M", manufacturer="Top Glove", supplier_id=suppliers[4].id,
                     category_id=cs_cat.id, unit_id=box_unit.id, material_type="consumable",
                     price=Decimal("250000"), lead_time_days=7, moq=50),
        ]
        session.add_all(materials_data)
        await session.flush()
        print(f"✅ Materials seeded ({len(materials_data)} materials)")

        # ============== Inventory (Initial stock) ==============
        loc_list = locations[:60]  # WH01 locations
        inventory_records = [
            Inventory(material_id=materials_data[0].id, location_id=loc_list[0].id, quantity=Decimal("8")),
            Inventory(material_id=materials_data[1].id, location_id=loc_list[1].id, quantity=Decimal("3")),
            Inventory(material_id=materials_data[2].id, location_id=loc_list[2].id, quantity=Decimal("5")),
            Inventory(material_id=materials_data[3].id, location_id=loc_list[3].id, quantity=Decimal("4")),
            Inventory(material_id=materials_data[4].id, location_id=loc_list[4].id, quantity=Decimal("6")),
            Inventory(material_id=materials_data[5].id, location_id=loc_list[5].id, quantity=Decimal("15")),
            Inventory(material_id=materials_data[6].id, location_id=loc_list[6].id, quantity=Decimal("25")),
            Inventory(material_id=materials_data[7].id, location_id=loc_list[10].id, quantity=Decimal("20")),
            Inventory(material_id=materials_data[8].id, location_id=loc_list[11].id, quantity=Decimal("50")),
            Inventory(material_id=materials_data[9].id, location_id=loc_list[12].id, quantity=Decimal("30")),
            Inventory(material_id=materials_data[10].id, location_id=loc_list[13].id, quantity=Decimal("15")),
            Inventory(material_id=materials_data[11].id, location_id=loc_list[14].id, quantity=Decimal("10")),
            Inventory(material_id=materials_data[12].id, location_id=loc_list[15].id, quantity=Decimal("100")),
        ]
        session.add_all(inventory_records)
        await session.flush()
        print(f"✅ Inventory seeded ({len(inventory_records)} records)")

        # ============== Min-Max ==============
        min_max_configs = [
            MaterialMinMax(material_id=materials_data[0].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("5"), max_quantity=Decimal("20"),
                          reorder_point=Decimal("8"), reorder_quantity=Decimal("10"), avg_daily_usage=Decimal("0.5")),
            MaterialMinMax(material_id=materials_data[1].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("2"), max_quantity=Decimal("10"),
                          reorder_point=Decimal("3"), reorder_quantity=Decimal("5"), avg_daily_usage=Decimal("0.1")),
            MaterialMinMax(material_id=materials_data[2].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("3"), max_quantity=Decimal("10"),
                          reorder_point=Decimal("4"), reorder_quantity=Decimal("5"), avg_daily_usage=Decimal("0.1")),
            MaterialMinMax(material_id=materials_data[5].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("10"), max_quantity=Decimal("50"),
                          reorder_point=Decimal("15"), reorder_quantity=Decimal("20"), avg_daily_usage=Decimal("1")),
            MaterialMinMax(material_id=materials_data[6].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("20"), max_quantity=Decimal("100"),
                          reorder_point=Decimal("30"), reorder_quantity=Decimal("50"), avg_daily_usage=Decimal("2")),
            MaterialMinMax(material_id=materials_data[7].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("10"), max_quantity=Decimal("50"),
                          reorder_point=Decimal("15"), reorder_quantity=Decimal("20"), avg_daily_usage=Decimal("1.5")),
            MaterialMinMax(material_id=materials_data[8].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("30"), max_quantity=Decimal("100"),
                          reorder_point=Decimal("40"), reorder_quantity=Decimal("50"), avg_daily_usage=Decimal("5")),
            MaterialMinMax(material_id=materials_data[10].id, warehouse_id=wh_main.id,
                          min_quantity=Decimal("20"), max_quantity=Decimal("80"),
                          reorder_point=Decimal("25"), reorder_quantity=Decimal("30"), avg_daily_usage=Decimal("3")),
        ]
        session.add_all(min_max_configs)
        await session.flush()
        print(f"✅ Min-Max configs seeded ({len(min_max_configs)} configs)")

        # ============== Phase 2: Production Lines ==============
        from datetime import date, timedelta

        lines = [
            ProductionLine(code="LINE-A", name="Line SMT A", name_en="SMT Line A",
                          area="SMT", manager="Trần Thị Sản Xuất"),
            ProductionLine(code="LINE-B", name="Line SMT B", name_en="SMT Line B",
                          area="SMT", manager="Trần Thị Sản Xuất"),
            ProductionLine(code="LINE-C", name="Line Assembly", name_en="Assembly Line",
                          area="Assembly", manager="Phạm Kỹ Sư"),
            ProductionLine(code="LINE-D", name="Line Testing & Packaging", name_en="Testing & Packaging Line",
                          area="Testing", manager="Vũ Chất Lượng"),
        ]
        session.add_all(lines)
        await session.flush()
        print("✅ Production Lines seeded (4 lines)")

        # ============== Phase 2: Machines ==============
        today = date.today()
        machines_data = [
            # Line A - SMT
            Machine(code="MC-A01", name="Máy in kem hàn DEK", name_en="DEK Solder Paste Printer",
                   machine_type="smt", model="DEK Horizon 03iX", manufacturer="ASM",
                   serial_number="DEK-2022-001", line_id=lines[0].id, location="Line A - Đầu line",
                   install_date=today - timedelta(days=730), status="running",
                   current_running_hours=Decimal("12500"), maintenance_interval_hours=2000,
                   last_maintenance_date=today - timedelta(days=15),
                   next_maintenance_date=today + timedelta(days=45),
                   specifications={"speed": "120 boards/hr", "accuracy": "±25μm"}),
            Machine(code="MC-A02", name="Máy gắn chip SMT Panasonic NPM-W2", name_en="Panasonic NPM-W2 Mounter",
                   machine_type="smt", model="NPM-W2", manufacturer="Panasonic",
                   serial_number="NPM-2021-015", line_id=lines[0].id, location="Line A - Giữa line",
                   install_date=today - timedelta(days=1095), status="running",
                   current_running_hours=Decimal("18200"), maintenance_interval_hours=3000,
                   last_maintenance_date=today - timedelta(days=30),
                   specifications={"speed": "76,000 cph", "heads": "16"}),
            Machine(code="MC-A03", name="Lò hàn Reflow Heller 1913 MK5", name_en="Heller Reflow Oven",
                   machine_type="smt", model="1913 MK5", manufacturer="Heller",
                   serial_number="HLR-2020-007", line_id=lines[0].id, location="Line A - Cuối line",
                   install_date=today - timedelta(days=1460), status="running",
                   current_running_hours=Decimal("22000"), maintenance_interval_hours=2500,
                   last_maintenance_date=today - timedelta(days=60),
                   specifications={"zones": "13", "max_temp": "350°C"}),
            # Line B - SMT
            Machine(code="MC-B01", name="Máy in kem hàn MPM Momentum", name_en="MPM Momentum Printer",
                   machine_type="smt", model="Momentum HiE", manufacturer="ITW EAE",
                   serial_number="MPM-2023-002", line_id=lines[1].id, location="Line B - Đầu line",
                   install_date=today - timedelta(days=365), status="running",
                   current_running_hours=Decimal("5800"), maintenance_interval_hours=2000),
            Machine(code="MC-B02", name="Máy gắn chip Fuji NXT III", name_en="Fuji NXT III Mounter",
                   machine_type="smt", model="NXT III", manufacturer="Fuji",
                   serial_number="FUJI-2022-008", line_id=lines[1].id, location="Line B - Giữa line",
                   install_date=today - timedelta(days=730), status="idle",
                   current_running_hours=Decimal("10500"), maintenance_interval_hours=3000,
                   last_maintenance_date=today - timedelta(days=7)),
            # Line C - Assembly
            Machine(code="MC-C01", name="Robot hàn Fanuc M-20iD/25", name_en="Fanuc Welding Robot",
                   machine_type="welding", model="M-20iD/25", manufacturer="Fanuc",
                   serial_number="FAN-2021-020", line_id=lines[2].id, location="Line C - Trạm 1",
                   install_date=today - timedelta(days=1095), status="running",
                   current_running_hours=Decimal("16800"), maintenance_interval_hours=5000,
                   last_maintenance_date=today - timedelta(days=45)),
            Machine(code="MC-C02", name="Máy vặn ốc tự động Janome", name_en="Janome Auto Screwdriver",
                   machine_type="assembly", model="JR3000", manufacturer="Janome",
                   serial_number="JAN-2022-005", line_id=lines[2].id, location="Line C - Trạm 3",
                   install_date=today - timedelta(days=730), status="running",
                   current_running_hours=Decimal("9200"), maintenance_interval_hours=4000),
            Machine(code="MC-C03", name="Máy ép nhiệt Hot Press", name_en="Hot Press Machine",
                   machine_type="press", model="HP-500T", manufacturer="Towa",
                   serial_number="TOW-2020-011", line_id=lines[2].id, location="Line C - Trạm 5",
                   install_date=today - timedelta(days=1460), status="broken",
                   current_running_hours=Decimal("24500"), maintenance_interval_hours=3000,
                   last_maintenance_date=today - timedelta(days=3)),
            # Line D - Testing & Packaging
            Machine(code="MC-D01", name="Máy kiểm tra AOI Omron VT-S730", name_en="Omron AOI VT-S730",
                   machine_type="testing", model="VT-S730", manufacturer="Omron",
                   serial_number="OMR-2022-003", line_id=lines[3].id, location="Line D - Kiểm tra",
                   install_date=today - timedelta(days=730), status="running",
                   current_running_hours=Decimal("11000"), maintenance_interval_hours=5000,
                   last_maintenance_date=today - timedelta(days=90)),
            Machine(code="MC-D02", name="Máy đóng gói tự động Omori", name_en="Omori Auto Packing",
                   machine_type="packaging", model="STN-7500", manufacturer="Omori",
                   serial_number="OMO-2023-001", line_id=lines[3].id, location="Line D - Đóng gói",
                   install_date=today - timedelta(days=365), status="maintenance",
                   current_running_hours=Decimal("6200"), maintenance_interval_hours=3000),
        ]
        session.add_all(machines_data)
        await session.flush()
        print(f"✅ Machines seeded ({len(machines_data)} machines)")

        # ============== Phase 2: Machine Parts ==============
        machine_parts = [
            # MC-A01 parts
            MachinePart(machine_id=machines_data[0].id, material_id=materials_data[0].id,
                       position="Head Sensor", lifetime_hours=Decimal("8000"),
                       current_hours=Decimal("6800"), lifetime_percentage=Decimal("15.00"),
                       installed_date=today - timedelta(days=400), status="warning",
                       serial_number="SNS-A01-001"),
            MachinePart(machine_id=machines_data[0].id, material_id=materials_data[5].id,
                       position="Main Belt", lifetime_hours=Decimal("5000"),
                       current_hours=Decimal("4800"), lifetime_percentage=Decimal("4.00"),
                       installed_date=today - timedelta(days=300), status="critical",
                       serial_number="BLT-A01-001"),
            # MC-A02 parts
            MachinePart(machine_id=machines_data[1].id, material_id=materials_data[1].id,
                       position="Servo Driver Head 1", lifetime_hours=Decimal("20000"),
                       current_hours=Decimal("15000"), lifetime_percentage=Decimal("25.00"),
                       installed_date=today - timedelta(days=900), status="warning",
                       serial_number="SRV-A02-001"),
            MachinePart(machine_id=machines_data[1].id, material_id=materials_data[4].id,
                       position="Motor X-axis", lifetime_hours=Decimal("20000"),
                       current_hours=Decimal("8000"), lifetime_percentage=Decimal("60.00"),
                       installed_date=today - timedelta(days=500), status="active",
                       serial_number="MTR-A02-001"),
            MachinePart(machine_id=machines_data[1].id, material_id=materials_data[6].id,
                       position="Bearing Y-axis", lifetime_hours=Decimal("10000"),
                       current_hours=Decimal("9800"), lifetime_percentage=Decimal("2.00"),
                       installed_date=today - timedelta(days=600), status="critical",
                       serial_number="BRG-A02-001"),
            # MC-A03 parts
            MachinePart(machine_id=machines_data[2].id, material_id=materials_data[0].id,
                       position="Temperature Sensor Zone 5", lifetime_hours=Decimal("8000"),
                       current_hours=Decimal("3000"), lifetime_percentage=Decimal("62.50"),
                       installed_date=today - timedelta(days=200), status="active",
                       serial_number="SNS-A03-001"),
            # MC-B02 parts
            MachinePart(machine_id=machines_data[4].id, material_id=materials_data[2].id,
                       position="Vision Camera", lifetime_hours=Decimal("15000"),
                       current_hours=Decimal("10500"), lifetime_percentage=Decimal("30.00"),
                       installed_date=today - timedelta(days=730), status="warning",
                       serial_number="CAM-B02-001"),
            # MC-C01 parts
            MachinePart(machine_id=machines_data[5].id, material_id=materials_data[4].id,
                       position="Welding Arm Motor", lifetime_hours=Decimal("20000"),
                       current_hours=Decimal("2000"), lifetime_percentage=Decimal("90.00"),
                       installed_date=today - timedelta(days=120), status="active",
                       serial_number="MTR-C01-001"),
            MachinePart(machine_id=machines_data[5].id, material_id=materials_data[5].id,
                       position="Feed Belt", lifetime_hours=Decimal("5000"),
                       current_hours=Decimal("5000"), lifetime_percentage=Decimal("0.00"),
                       installed_date=today - timedelta(days=350), status="expired",
                       serial_number="BLT-C01-001"),
            # MC-C03 parts (broken machine)
            MachinePart(machine_id=machines_data[7].id, material_id=materials_data[3].id,
                       position="Main PLC", lifetime_hours=Decimal("30000"),
                       current_hours=Decimal("24500"), lifetime_percentage=Decimal("18.33"),
                       installed_date=today - timedelta(days=1460), status="warning",
                       serial_number="PLC-C03-001"),
            # MC-D01 parts
            MachinePart(machine_id=machines_data[8].id, material_id=materials_data[2].id,
                       position="AOI Camera Main", lifetime_hours=Decimal("15000"),
                       current_hours=Decimal("11000"), lifetime_percentage=Decimal("26.67"),
                       installed_date=today - timedelta(days=730), status="warning",
                       serial_number="CAM-D01-001"),
        ]
        session.add_all(machine_parts)
        await session.flush()
        print(f"✅ Machine Parts seeded ({len(machine_parts)} parts)")

        # ============== Phase 2: Maintenance Logs ==============
        maint_user = users[3]  # maintenance user
        eng_user = users[4]    # engineering user

        maint_logs = [
            MaintenanceLog(log_number="ML-001", machine_id=machines_data[0].id,
                          maintenance_type="preventive", maintenance_date=today - timedelta(days=15),
                          shift="A", running_hours_at_time=Decimal("12200"),
                          description="Bảo trì định kỳ máy in kem hàn DEK. Vệ sinh stencil, kiểm tra alignment.",
                          action_taken="Vệ sinh head, calibrate alignment, thay dầu bôi trơn.",
                          downtime_hours=Decimal("4"), performed_by=maint_user.id, status="completed"),
            MaintenanceLog(log_number="ML-002", machine_id=machines_data[1].id,
                          maintenance_type="corrective", maintenance_date=today - timedelta(days=30),
                          shift="B", running_hours_at_time=Decimal("17800"),
                          description="Servo driver Head 1 báo lỗi E50. Máy dừng đột ngột.",
                          root_cause="Servo driver quá nhiệt do quạt tản nhiệt bị bụi.",
                          action_taken="Vệ sinh quạt tản nhiệt, reset alarm. Theo dõi thêm.",
                          downtime_hours=Decimal("6"), performed_by=maint_user.id, status="completed"),
            MaintenanceLog(log_number="ML-003", machine_id=machines_data[2].id,
                          maintenance_type="corrective", maintenance_date=today - timedelta(days=60),
                          shift="A", running_hours_at_time=Decimal("21500"),
                          description="Nhiệt độ zone 7 không ổn định, sai lệch ±5°C.",
                          root_cause="Thermocouple bị lão hóa.",
                          action_taken="Thay thermocouple zone 7, calibrate lại nhiệt độ.",
                          downtime_hours=Decimal("3"), performed_by=eng_user.id, status="completed"),
            MaintenanceLog(log_number="ML-004", machine_id=machines_data[7].id,
                          maintenance_type="emergency", maintenance_date=today - timedelta(days=3),
                          shift="A", running_hours_at_time=Decimal("24500"),
                          description="Máy ép nhiệt dừng khẩn cấp. Xylanh chính bị kẹt, rò rỉ dầu thủy lực.",
                          root_cause="Phớt xylanh chính bị mòn, gây rò rỉ dầu và mất áp suất.",
                          action_taken="Tạm dừng máy, chờ linh kiện thay thế từ NCC.",
                          downtime_hours=Decimal("72"), performed_by=maint_user.id, status="open"),
            MaintenanceLog(log_number="ML-005", machine_id=machines_data[4].id,
                          maintenance_type="preventive", maintenance_date=today - timedelta(days=7),
                          shift="A", running_hours_at_time=Decimal("10500"),
                          description="PM định kỳ. Kiểm tra nozzle, feeder, vision camera.",
                          action_taken="Vệ sinh nozzle, calibrate camera, bôi mỡ trượt.",
                          downtime_hours=Decimal("3"), performed_by=eng_user.id, status="completed"),
            MaintenanceLog(log_number="ML-006", machine_id=machines_data[8].id,
                          maintenance_type="predictive", maintenance_date=today - timedelta(days=90),
                          shift="B", running_hours_at_time=Decimal("9500"),
                          description="Kiểm tra dự đoán: camera AOI có dấu hiệu giảm độ nét.",
                          action_taken="Vệ sinh lens, kiểm tra cáp kết nối. Đề xuất thay camera trong 2 tháng tới.",
                          downtime_hours=Decimal("2"), performed_by=eng_user.id, status="completed"),
        ]
        session.add_all(maint_logs)
        await session.flush()

        # Maintenance log items (parts used)
        maint_items = [
            MaintenanceLogItem(log_id=maint_logs[0].id, material_id=materials_data[11].id,
                              quantity=Decimal("1"), action_type="consumed", note="Mỡ bôi trơn cho rail"),
            MaintenanceLogItem(log_id=maint_logs[2].id, material_id=materials_data[0].id,
                              quantity=Decimal("1"), action_type="replaced", note="Thay thermocouple zone 7"),
            MaintenanceLogItem(log_id=maint_logs[4].id, material_id=materials_data[11].id,
                              quantity=Decimal("0.5"), action_type="consumed", note="Mỡ bôi trơn"),
            MaintenanceLogItem(log_id=maint_logs[4].id, material_id=materials_data[9].id,
                              quantity=Decimal("2"), action_type="consumed", note="Khăn lau vệ sinh"),
        ]
        session.add_all(maint_items)
        await session.flush()
        print(f"✅ Maintenance Logs seeded ({len(maint_logs)} logs, {len(maint_items)} items)")

        # ============== Phase 2: Running Hours (last 7 days) ==============
        running_records = []
        for day_offset in range(7, 0, -1):
            record_date = today - timedelta(days=day_offset)
            for i, machine in enumerate(machines_data):
                if machine.status in ("broken", "maintenance", "decommissioned"):
                    hours = Decimal("0") if machine.status == "broken" and day_offset <= 3 else Decimal(str(round(6 + (i % 4) * 1.5, 1)))
                elif machine.status == "idle":
                    hours = Decimal(str(round(4 + (day_offset % 3), 1)))
                else:
                    hours = Decimal(str(round(7 + (i % 5) * 0.8 + (day_offset % 3) * 0.5, 1)))

                cumulative = machine.current_running_hours - Decimal(str(day_offset)) * Decimal("8") + hours
                running_records.append(
                    MachineRunningHour(
                        machine_id=machine.id,
                        record_date=record_date,
                        running_hours=hours,
                        cumulative_hours=max(cumulative, Decimal("0")),
                        shift=None,
                        recorded_by=users[1].id,  # warehouse user
                    )
                )
        session.add_all(running_records)
        await session.flush()
        print(f"✅ Running Hours seeded ({len(running_records)} records)")

        await session.commit()
        print("\n🎉 Database seeding completed successfully (Phase 1 + Phase 2)!")


if __name__ == "__main__":
    asyncio.run(seed_database())
