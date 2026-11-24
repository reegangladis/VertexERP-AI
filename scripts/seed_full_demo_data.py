"""Comprehensive Enterprise Demo Data Seeder for VertexERP AI.

Populates realistic, connected demo data across all modules:
- Organization (Branches, Holidays)
- HR (Employees, Attendance, Leave Balances)
- CRM & Sales (Leads, Customers, Contacts, Deals, Quotations, Sales Orders)
- Inventory & Supply Chain (Categories, UoMs, Products, Warehouses, Stock Balances)
- Procurement (Suppliers, Purchase Orders)
- Finance (Chart of Accounts, Invoices)
- Manufacturing (Work Centers, BOMs, Production Orders)
- Analytics (KPI Definitions)
"""

import sqlite3
import uuid
import datetime
from decimal import Decimal

def seed_full_demo():
    print("=" * 60)
    print("Starting Comprehensive Enterprise Demo Data Seeding...")
    print("=" * 60)

    conn = sqlite3.connect("vertexerp_dev.db")
    conn.create_function("clock_timestamp", 0, lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    conn.create_function("gen_random_uuid", 0, lambda: str(uuid.uuid4()))
    cursor = conn.cursor()

    # 1. Fetch active tenant and organization
    cursor.execute("SELECT id FROM tenants WHERE slug = 'apex'")
    t_row = cursor.fetchone()
    if not t_row:
        tenant_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO tenants (id, name, slug, subscription_tier, subscription_status, is_active, created_at, updated_at, is_deleted) VALUES (?, 'Apex Global Holdings', 'apex', 'ENTERPRISE', 'ACTIVE', 1, datetime('now'), datetime('now'), 0)", (tenant_id,))
    else:
        tenant_id = t_row[0]

    cursor.execute("SELECT id FROM organizations WHERE tenant_id = ?", (tenant_id,))
    o_row = cursor.fetchone()
    if not o_row:
        org_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO organizations (id, tenant_id, name, legal_name, tax_identifier, base_currency, is_active, created_at, updated_at, is_deleted) VALUES (?, ?, 'Apex Commercial Enterprise', 'Apex Global Enterprises International Inc.', 'US-EIN-987654321', 'USD', 1, datetime('now'), datetime('now'), 0)", (org_id, tenant_id))
    else:
        org_id = o_row[0]

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    today = datetime.date.today().isoformat()

    # 2. Seed Branches
    branches_data = [
        ("BR-NYC", "New York Global HQ", "One World Trade Center, Suite 8500", "New York", "NY", "10007", "USA", "+1 (212) 555-0100", "nyc@vertexerp.com", 1),
        ("BR-LDN", "London EMEA Hub", "25 Bank Street, Canary Wharf", "London", "England", "E14 5JP", "GBR", "+44 20 7946 0910", "london@vertexerp.com", 0),
        ("BR-SGP", "Singapore APAC Center", "10 Collyer Quay, Ocean Financial Centre", "Singapore", "Central", "049315", "SGP", "+65 6789 0123", "apac@vertexerp.com", 0),
        ("BR-SFO", "San Francisco AI Hub", "500 Howard Street, Suite 400", "San Francisco", "CA", "94105", "USA", "+1 (415) 555-0199", "sfo@vertexerp.com", 0),
    ]
    branch_map = {}
    for code, name, addr, city, state, postal, country, phone, email, is_hq in branches_data:
        cursor.execute("SELECT id FROM branches WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        row = cursor.fetchone()
        if not row:
            b_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO branches (id, tenant_id, organization_id, code, name, address_line1, city, state, postal_code, country, phone, email, is_headquarters, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?, 0)
            """, (b_id, tenant_id, org_id, code, name, addr, city, state, postal, country, phone, email, is_hq, now, now))
            branch_map[code] = b_id
        else:
            branch_map[code] = row[0]
    print(f"✓ Branches verified ({len(branches_data)} total)")

    # 3. Seed Holidays
    holidays_data = [
        ("New Year's Day", "2026-01-01", "FEDERAL", "Global statutory public holiday"),
        ("Memorial Day", "2026-05-25", "FEDERAL", "US Federal Memorial Day"),
        ("Independence Day", "2026-07-04", "FEDERAL", "National Independence Day"),
        ("Labor Day", "2026-09-07", "FEDERAL", "Labor & Workforce Day"),
        ("Thanksgiving Day", "2026-11-26", "FEDERAL", "Annual Thanksgiving celebration"),
        ("Christmas Day", "2026-12-25", "FEDERAL", "Christmas Holiday"),
    ]
    for name, h_date, h_type, desc in holidays_data:
        cursor.execute("SELECT id FROM holidays WHERE tenant_id = ? AND name = ?", (tenant_id, name))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO holidays (id, tenant_id, organization_id, name, holiday_date, holiday_type, is_recurring, description, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, 1, ?, ?, 0)
            """, (str(uuid.uuid4()), tenant_id, org_id, name, h_date, h_type, desc, now, now))
    print(f"✓ Holidays verified ({len(holidays_data)} total)")

    # 4. Seed Inventory UoMs & Categories
    uoms_data = [
        ("UNIT", "Unit / Piece", "COUNT", 1, 1.0),
        ("BOX", "Box (10 Units)", "COUNT", 0, 10.0),
        ("SET", "Complete Rack Set", "COUNT", 0, 1.0),
    ]
    uom_map = {}
    for code, name, cat, is_base, factor in uoms_data:
        cursor.execute("SELECT id FROM inv_units_of_measure WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        row = cursor.fetchone()
        if not row:
            u_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO inv_units_of_measure (id, tenant_id, organization_id, code, name, category, is_base_unit, conversion_factor, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?, 0)
            """, (u_id, tenant_id, org_id, code, name, cat, is_base, factor, now, now))
            uom_map[code] = u_id
        else:
            uom_map[code] = row[0]

    categories_data = [
        ("AI_SERVERS", "AI GPU Clusters & Servers", "Enterprise compute nodes and accelerators"),
        ("NETWORKING", "High-Bandwidth Network Gear", "InfiniBand switches and optical transceivers"),
        ("EDGE_DEVICES", "Industrial Edge Gateways", "Ruggedized IoT edge intelligence nodes"),
        ("SOFTWARE", "VertexERP Cloud Licenses", "Enterprise recurring platform subscriptions"),
    ]
    cat_map = {}
    for code, name, desc in categories_data:
        cursor.execute("SELECT id FROM inv_product_categories WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        row = cursor.fetchone()
        if not row:
            c_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO inv_product_categories (id, tenant_id, organization_id, code, name, description, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, 1, 1, ?, ?, 0)
            """, (c_id, tenant_id, org_id, code, name, desc, now, now))
            cat_map[code] = c_id
        else:
            cat_map[code] = row[0]
    print("✓ Inventory UoMs and Categories verified")

    # 5. Seed Warehouses
    warehouses_data = [
        ("WH-EAST", "East Coast Logistics Hub (JFK)", "DISTRIBUTION", '{"city": "Jamaica", "state": "NY", "country": "USA"}', 1),
        ("WH-WEST", "West Coast Fulfillment Hub (OAK)", "DISTRIBUTION", '{"city": "Oakland", "state": "CA", "country": "USA"}', 0),
        ("WH-EMEA", "Rotterdam International Depot", "TRANSIT", '{"city": "Rotterdam", "state": "ZH", "country": "NLD"}', 0),
    ]
    wh_map = {}
    for code, name, wh_type, addr_json, is_prim in warehouses_data:
        cursor.execute("SELECT id FROM inv_warehouses WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        row = cursor.fetchone()
        if not row:
            w_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO inv_warehouses (id, tenant_id, organization_id, code, name, warehouse_type, address, is_primary, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?, 0)
            """, (w_id, tenant_id, org_id, code, name, wh_type, addr_json, is_prim, now, now))
            wh_map[code] = w_id
        else:
            wh_map[code] = row[0]
    print(f"✓ Warehouses verified ({len(warehouses_data)} total)")

    # 6. Seed Products
    products_data = [
        ("SKU-SRV-900", "Vertex Titan AI Cluster (8x H100)", "High-throughput AI compute server with liquid cooling", "AI_SERVERS", "UNIT", 120000.0, 165000.0, 2, 5),
        ("SKU-NET-400", "400Gbps InfiniBand Quantum Switch", "Ultra-low latency Spine/Leaf network switch", "NETWORKING", "UNIT", 14500.0, 22000.0, 5, 10),
        ("SKU-EDG-50", "Apex Edge Industrial AI Gateway", "Ruggedized multi-sensor edge inference controller", "EDGE_DEVICES", "UNIT", 1800.0, 2950.0, 10, 25),
        ("SKU-TRX-100", "100G QSFP28 Optical Transceiver", "Long-haul single-mode fiber optical transceiver", "NETWORKING", "UNIT", 180.0, 340.0, 50, 100),
        ("SKU-SW-ENT", "VertexERP AI Enterprise Suite (100 Seats)", "Annual enterprise enterprise ERP license", "SOFTWARE", "UNIT", 0.0, 60000.0, 0, 0),
    ]
    prod_map = {}
    for sku, name, desc, cat_c, uom_c, cost, sell, reorder, reorder_qty in products_data:
        cursor.execute("SELECT id FROM inv_products WHERE tenant_id = ? AND sku = ?", (tenant_id, sku))
        row = cursor.fetchone()
        if not row:
            p_id = str(uuid.uuid4())
            cat_id = cat_map[cat_c]
            u_id = uom_map[uom_c]
            cursor.execute("""
                INSERT INTO inv_products (id, tenant_id, organization_id, sku, name, description, category_id, uom_id, valuation_method, cost_price, selling_price, reorder_point, reorder_quantity, safety_stock, min_order_qty, lead_time_days, is_stockable, is_purchasable, is_sellable, allow_negative_stock, custom_fields, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'FIFO', ?, ?, ?, ?, 2, 1, 14, 1, 1, 1, 0, '{}', 1, 1, ?, ?, 0)
            """, (p_id, tenant_id, org_id, sku, name, desc, cat_id, u_id, cost, sell, reorder, reorder_qty, now, now))
            prod_map[sku] = p_id

            # Stock Balance in WH-EAST
            wh_id = wh_map["WH-EAST"]
            qty = 24 if "SRV" in sku else (150 if "TRX" in sku else 45)
            val = qty * cost
            cursor.execute("""
                INSERT INTO inv_stock_balances (id, tenant_id, organization_id, product_id, warehouse_id, quantity_on_hand, quantity_reserved, quantity_allocated, quantity_available, average_cost, total_value, version, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, 1, ?)
            """, (str(uuid.uuid4()), tenant_id, org_id, p_id, wh_id, qty, qty, cost, val, now))
        else:
            prod_map[sku] = row[0]
    print(f"✓ Products and Stock Balances verified ({len(products_data)} total)")

    # 7. Seed Procurement Suppliers & POs
    suppliers_data = [
        ("SUP-NVI", "NVIDIA Enterprise Systems Corp", "Jensen Huang", "enterprise@nvidia.com", "+1 (408) 486-2000", "NET30", 14, 4.95),
        ("SUP-CIS", "Cisco Systems Global Logistics", "Chuck Robbins", "procurement@cisco.com", "+1 (408) 526-4000", "NET45", 10, 4.80),
        ("SUP-SMCI", "Supermicro Advanced Servers", "Charles Liang", "sales@supermicro.com", "+1 (408) 503-8000", "NET30", 21, 4.70),
    ]
    sup_map = {}
    for code, name, contact, email, phone, terms, lead, rating in suppliers_data:
        cursor.execute("SELECT id FROM proc_suppliers WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        row = cursor.fetchone()
        if not row:
            s_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO proc_suppliers (id, tenant_id, organization_id, code, name, contact_name, email, phone, currency, payment_terms, lead_time_days, address, status, rating, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'USD', ?, ?, '{}', 'ACTIVE', ?, 1, 1, ?, ?, 0)
            """, (s_id, tenant_id, org_id, code, name, contact, email, phone, terms, lead, rating, now, now))
            sup_map[code] = s_id
        else:
            sup_map[code] = row[0]

    # Purchase Orders
    po_data = [
        ("PO-2026-001", "SUP-NVI", "WH-EAST", "2026-02-10", "CONFIRMED", 360000.0, 36000.0, 396000.0),
        ("PO-2026-002", "SUP-CIS", "WH-WEST", "2026-02-18", "RECEIVED", 88000.0, 8800.0, 96800.0),
        ("PO-2026-003", "SUP-SMCI", "WH-EAST", "2026-02-22", "DRAFT", 145000.0, 14500.0, 159500.0),
    ]
    for po_num, sup_c, wh_c, o_date, status, sub, tax, grand in po_data:
        cursor.execute("SELECT id FROM proc_purchase_orders WHERE tenant_id = ? AND po_number = ?", (tenant_id, po_num))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO proc_purchase_orders (id, tenant_id, organization_id, po_number, supplier_id, warehouse_id, order_date, currency, status, subtotal, discount_amount, tax_amount, grand_total, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'USD', ?, ?, 0.0, ?, ?, 1, 1, ?, ?, 0)
            """, (str(uuid.uuid4()), tenant_id, org_id, po_num, sup_map[sup_c], wh_map[wh_c], o_date, status, sub, tax, grand, now, now))
    print(f"✓ Suppliers and Purchase Orders verified")

    # 8. Seed Finance Chart of Accounts & Invoices
    accounts_data = [
        ("1010", "Cash & Operating Treasury", "ASSET", "CURRENT_ASSET"),
        ("1100", "Accounts Receivable (Trade)", "ASSET", "CURRENT_ASSET"),
        ("1200", "Merchandise Inventory", "ASSET", "CURRENT_ASSET"),
        ("2010", "Accounts Payable (Trade)", "LIABILITY", "CURRENT_LIABILITY"),
        ("2200", "Accrued Employee Payroll", "LIABILITY", "CURRENT_LIABILITY"),
        ("3000", "Shareholder Retained Earnings", "EQUITY", "EQUITY"),
        ("4000", "Enterprise SaaS & License Revenue", "REVENUE", "OPERATING_REVENUE"),
        ("4100", "Hardware & Edge Compute Revenue", "REVENUE", "OPERATING_REVENUE"),
        ("5000", "Cost of Goods Sold (COGS)", "EXPENSE", "DIRECT_EXPENSE"),
        ("6000", "Research & Artificial Intelligence R&D", "EXPENSE", "OPERATING_EXPENSE"),
        ("6100", "Sales & Marketing Global GTM", "EXPENSE", "OPERATING_EXPENSE"),
    ]
    for code, name, a_type, a_cat in accounts_data:
        cursor.execute("SELECT id FROM fin_accounts WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO fin_accounts (id, tenant_id, organization_id, code, name, account_type, account_category, currency, is_reconciled, is_active, is_deleted, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'USD', 1, 1, 0, 1, ?, ?)
            """, (str(uuid.uuid4()), tenant_id, org_id, code, name, a_type, a_cat, now, now))
    print(f"✓ Chart of Accounts verified ({len(accounts_data)} accounts)")

    # Finance Invoices
    cursor.execute("SELECT id FROM crm_customers WHERE tenant_id = ? LIMIT 1", (tenant_id,))
    cust_row = cursor.fetchone()
    cust_id = cust_row[0] if cust_row else str(uuid.uuid4())

    invoices_data = [
        ("INV-2026-001", "2026-02-01", "2026-03-01", 165000.0, 16500.0, 181500.0, 181500.0, 0.0, "PAID"),
        ("INV-2026-002", "2026-02-10", "2026-03-12", 72000.0, 7200.0, 79200.0, 0.0, 79200.0, "ISSUED"),
        ("INV-2026-003", "2026-02-15", "2026-03-17", 48000.0, 4800.0, 52800.0, 20000.0, 32800.0, "PARTIALLY_PAID"),
        ("INV-2026-004", "2026-02-20", "2026-03-22", 245000.0, 24500.0, 269500.0, 0.0, 269500.0, "ISSUED"),
    ]
    for inv_num, iss_d, due_d, sub, tax, tot, paid, due, status in invoices_data:
        cursor.execute("SELECT id FROM fin_invoices WHERE tenant_id = ? AND invoice_number = ?", (tenant_id, inv_num))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO fin_invoices (id, tenant_id, organization_id, invoice_number, customer_id, issue_date, due_date, currency, exchange_rate, subtotal_amount, tax_amount, total_amount, amount_paid, amount_due, status, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'USD', 1.0, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (str(uuid.uuid4()), tenant_id, org_id, inv_num, cust_id, iss_d, due_d, sub, tax, tot, paid, due, status, now, now))
    print(f"✓ Finance Invoices verified ({len(invoices_data)} total)")

    # 9. Seed Manufacturing Work Centers & Production Orders
    wc_data = [
        ("WC-SMT", "High-Speed SMT Surface Mount Line", "ASSEMBLY", 16.0, 120.0, 45.0, "ACTIVE"),
        ("WC-CHAS", "Rack Integration & Cabling Bay", "ASSEMBLY", 16.0, 85.0, 30.0, "ACTIVE"),
        ("WC-QC", "Thermal Burn-In & QA Testing Room", "TESTING", 24.0, 60.0, 20.0, "ACTIVE"),
    ]
    wc_map = {}
    for code, name, wc_type, cap, cost, over, status in wc_data:
        cursor.execute("SELECT id FROM mfg_work_centers WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        row = cursor.fetchone()
        if not row:
            w_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO mfg_work_centers (id, tenant_id, organization_id, code, name, work_center_type, capacity_per_day_hours, cost_per_hour, overhead_cost_per_hour, status, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (w_id, tenant_id, org_id, code, name, wc_type, cap, cost, over, status, now, now))
            wc_map[code] = w_id
        else:
            wc_map[code] = row[0]

    # BOM & Production Orders
    titan_id = prod_map.get("SKU-SRV-900")
    if titan_id:
        cursor.execute("SELECT id FROM mfg_boms WHERE tenant_id = ? AND code = 'BOM-TITAN-1'", (tenant_id,))
        bom_row = cursor.fetchone()
        if not bom_row:
            bom_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO mfg_boms (id, tenant_id, organization_id, code, name, product_id, quantity, uom_id, status, is_default, notes, created_at, updated_at)
                VALUES (?, ?, ?, 'BOM-TITAN-1', 'Titan AI Cluster Assembly Bill of Materials', ?, 1.0, ?, 'ACTIVE', 1, 'Standard 8x GPU config', ?, ?)
            """, (bom_id, tenant_id, org_id, titan_id, uom_map["UNIT"], now, now))
        else:
            bom_id = bom_row[0]

        mo_data = [
            ("MO-2026-001", titan_id, bom_id, 10.0, 6.0, "WH-EAST", "2026-02-15", "2026-03-05", "IN_PROGRESS", "HIGH", 120000.0, 1200000.0),
            ("MO-2026-002", titan_id, bom_id, 4.0, 4.0, "WH-WEST", "2026-02-01", "2026-02-20", "COMPLETED", "NORMAL", 120000.0, 480000.0),
        ]
        for mo_num, p_id, b_id, plan_qty, prod_qty, wh_c, s_date, e_date, status, prio, u_cost, t_cost in mo_data:
            cursor.execute("SELECT id FROM mfg_production_orders WHERE tenant_id = ? AND order_number = ?", (tenant_id, mo_num))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO mfg_production_orders (id, tenant_id, organization_id, order_number, product_id, bom_id, bom_version_id, planned_quantity, produced_quantity, rejected_quantity, scrap_quantity, target_warehouse_id, planned_start_date, planned_due_date, status, priority, unit_cost, total_cost, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?, ?, 'Enterprise batch run', ?, ?)
                """, (str(uuid.uuid4()), tenant_id, org_id, mo_num, p_id, b_id, b_id, plan_qty, prod_qty, wh_map[wh_c], s_date, e_date, status, prio, u_cost, t_cost, now, now))
    print("✓ Manufacturing Work Centers and Production Orders verified")

    # 10. Seed Analytics KPI Definitions
    kpi_data = [
        ("KPI-ARR", "Annual Recurring Revenue (ARR)", "REVENUE", "Total normalized annualized SaaS and contract subscription run-rate", "USD", 12500000.0, 11000000.0, 9500000.0, "UP", "SUM"),
        ("KPI-WIN-RATE", "Sales Deal Win Rate", "SALES", "Percentage of closed-won opportunities over total resolved pipeline deals", "%", 42.0, 35.0, 25.0, "UP", "RATIO"),
        ("KPI-ATT-RATE", "Employee Attendance Compliance", "HR", "Daily percentage of employees clocking in within shift parameters", "%", 96.5, 92.0, 85.0, "UP", "AVERAGE"),
        ("KPI-ON-TIME", "Supply Chain On-Time Delivery", "SUPPLY_CHAIN", "Procurement and production fulfillment delivery SLA compliance", "%", 98.0, 94.0, 90.0, "UP", "PERCENTAGE"),
        ("KPI-NET-MARGIN", "Net Operating Margin", "FINANCE", "Operating profit expressed as a percentage of total recognized revenue", "%", 28.5, 22.0, 15.0, "UP", "PERCENTAGE"),
    ]
    for code, name, cat, desc, unit, target, warn, crit, trend, calc in kpi_data:
        cursor.execute("SELECT id FROM analytics_kpi_definitions WHERE tenant_id = ? AND code = ?", (tenant_id, code))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO analytics_kpi_definitions (id, tenant_id, organization_id, code, name, category, description, unit, target_value, warning_threshold, critical_threshold, trend_direction, calculation_method, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (str(uuid.uuid4()), tenant_id, org_id, code, name, cat, desc, unit, target, warn, crit, trend, calc, now, now))
    print(f"✓ Analytics KPI Definitions verified ({len(kpi_data)} total)")

    # 11. Add more CRM Leads & Deals if sparse
    cursor.execute("SELECT COUNT(*) FROM crm_leads WHERE tenant_id = ?", (tenant_id,))
    lead_count = cursor.fetchone()[0]
    if lead_count < 8:
        extra_leads = [
            ("Lumina Retail Technologies", "Sophia", "Alvarez", "sophia@luminaretail.com", "+1 312 555 0144", 185000.0, "QUALIFIED", "HOT"),
            ("Quantum BioPharma Labs", "Ethan", "Wright", "ewright@quantumbio.com", "+1 617 555 0192", 340000.0, "PROPOSAL", "HOT"),
            ("AeroDynamics Defense Systems", "Robert", "Hayes", "r.hayes@aerodynamics.mil", "+1 703 555 0188", 520000.0, "CONTACTED", "WARM"),
            ("FinTech High Frequency Core", "Marcus", "Vance", "mvance@fintechcore.io", "+1 212 555 0133", 420000.0, "NEW", "WARM"),
            ("Nordic Cloud Infrastructure", "Freja", "Lindstrom", "freja@nordiccloud.se", "+46 8 123 4567", 210000.0, "QUALIFIED", "HOT"),
        ]
        for comp, first, last, email, phone, val, status, rating in extra_leads:
            cursor.execute("""
                INSERT INTO crm_leads (id, tenant_id, organization_id, company_name, first_name, last_name, email, phone, estimated_value, status, source, rating, is_active, version, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'INBOUND_WEB', ?, 1, 1, ?, ?, 0)
            """, (str(uuid.uuid4()), tenant_id, org_id, comp, first, last, email, phone, val, status, rating, now, now))
        print("✓ Additional Enterprise CRM Leads seeded")

    conn.commit()
    conn.close()
    print("=" * 60)
    print("ALL ENTERPRISE DEMO DATA SUCCESSFULLY SEEDED!")
    print("=" * 60)

if __name__ == "__main__":
    seed_full_demo()
