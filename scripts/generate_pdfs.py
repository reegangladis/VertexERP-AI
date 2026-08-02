import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Resolve docs/ relative to the repo root (parent of this scripts/ directory)
# instead of a hardcoded machine-specific path, so this runs on any machine/OS.
DOCS_DIR = str(Path(__file__).resolve().parent.parent / "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

def create_pdf(filename, title, subtitle, content_blocks):
    filepath = os.path.join(DOCS_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=4,
        spaceAfter=4
    )
    
    story = [
        Paragraph(title, title_style),
        Paragraph(subtitle, subtitle_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10)
    ]
    
    for block in content_blocks:
        b_type = block[0]
        if b_type == 'h2':
            story.append(Paragraph(block[1], h2_style))
        elif b_type == 'body':
            story.append(Paragraph(block[1], body_style))
        elif b_type == 'code':
            story.append(Paragraph(block[1].replace('\n', '<br/>'), code_style))
        elif b_type == 'table':
            headers = block[1]
            rows = block[2]
            table_data = [[Paragraph(f"<b>{h}</b>", body_style) for h in headers]]
            for r in rows:
                table_data.append([Paragraph(str(cell), body_style) for cell in r])
            
            t = Table(table_data, colWidths=block[3] if len(block) > 3 else None)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
        elif b_type == 'spacer':
            story.append(Spacer(1, block[1]))
            
    doc.build(story)
    print(f"Successfully generated {filepath}")

def generate_system_architecture_pdf():
    content = [
        ('h2', '1. Executive Architecture Overview'),
        ('body', 'VertexERP AI is built as a multi-tenant, cloud-native Enterprise Resource Planning and AI Operating System. The platform combines high-throughput transactional ERP capabilities (General Ledger, MES, CRM, Supply Chain, HR) with real-time vector RAG intelligence, MLOps model training, and automated multi-step workflow DAG execution.'),
        ('h2', '2. Cloud Deployment Topology'),
        ('code', 'Global Geo-DNS / Anycast CDN / OWASP WAF DDoS Guard\n  ├── US East (AWS EKS Primary Cluster)\n  ├── EU Central (AWS EKS Secondary Active)\n  └── APAC (Azure AKS Active Replica)\n      ├── API Gateway (FastAPI Uvicorn Async Workers)\n      ├── Enterprise React 19 Frontend Web Portal (Vite / Tailwind)\n      ├── PostgreSQL 17 Multi-Region Database (PgVector Enabled)\n      ├── Redis 7 Cluster (Distributed Session & RBAC Cache)\n      └── FAISS Vector Store (Enterprise Document Embeddings)'),
        ('h2', '3. Platform Module Architecture Matrix'),
        ('table', 
            ['Module Domain', 'Core Responsibility', 'Technology Stack'],
            [
                ['Organization Isolation', 'Multi-tenant isolation, subsidiaries, cost centers', 'SQLAlchemy 2 Async, PostgreSQL 17'],
                ['Identity & Security', 'OAuth2, JWT bearer, RBAC, ABAC, Security Telemetry', 'FastAPI Security, Passlib, Cryptography'],
                ['HR & Payroll Intelligence', 'Employee lifecycle, time tracking, payroll calculation', 'Pandas, NumPy, Async Repositories'],
                ['CRM & Pipeline', 'Lead tracking, deal forecasting, ticket resolution', 'Scikit-Learn, LightGBM, SQLAlchemy'],
                ['Inventory & Logistics', 'Multi-warehouse stock, serial/lot tracking, valuations', 'Redis Cache, PostgreSQL B-Tree Indexes'],
                ['Finance Platform', 'Double-entry GL, invoicing, accounts payable/receivable', 'SQLAlchemy Async Transactions, Alembic'],
                ['Manufacturing MES', 'Bill of Materials (BOM), Work Orders, OEE Analytics', 'Async Worker Queue, Manufacturing Engine'],
                ['Enterprise RAG', 'Vector search, document chunking, citation retrieval', 'FAISS, PgVector, SentenceTransformers'],
                ['AI Copilot Agent', 'Intent classification, tool execution, NL to SQL', 'LangChain, Structured Tool Registry'],
                ['MLOps & ML Studio', 'AutoML, hyperparameter tuning, model registry', 'Scikit-learn, XGBoost, SHAP, MLflow']
            ],
            [120, 240, 180]
        ),
        ('h2', '4. Security & Compliance Controls'),
        ('body', 'Enforces strict OWASP Top 10 defenses including Content Security Policy (CSP), HTTP Strict Transport Security (HSTS), AES-256-GCM data encryption at rest, TLS 1.3 in transit, automated HMAC SHA-256 webhook signatures, and immutable SOC 2 audit logging.')
    ]
    create_pdf('SYSTEM_ARCHITECTURE.pdf', 'VertexERP AI — System Architecture Specification', 'Production Engineering & Multi-Cloud Infrastructure Blueprint', content)

def generate_database_schema_pdf():
    content = [
        ('h2', '1. Relational Schema Architecture'),
        ('body', 'VertexERP AI operates over 90+ normalized relational entities in PostgreSQL 17. Every table enforces strict tenant isolation using an indexed organization_id foreign key, standard UUID primary keys, UTC timestamps (created_at, updated_at), and soft delete flag (is_deleted).'),
        ('h2', '2. Core Entity Relationship Specifications'),
        ('table',
            ['Table Name', 'Primary Key', 'Foreign Keys / Indexes', 'Key Attributes'],
            [
                ['organizations', 'id (UUID)', 'slug (UNIQUE INDEX)', 'name, slug, currency, status'],
                ['users', 'id (UUID)', 'organization_id, role_id', 'email (UNIQUE), password_hash, is_active'],
                ['employees', 'id (UUID)', 'organization_id, department_id', 'employee_code, first_name, designation, salary'],
                ['customers', 'id (UUID)', 'organization_id', 'customer_code, company_name, email, phone'],
                ['products', 'id (UUID)', 'organization_id, category_id', 'sku (UNIQUE), name, unit_price, cost_price'],
                ['customer_invoices', 'id (UUID)', 'organization_id, customer_id', 'invoice_number, total_amount, status, due_date'],
                ['bill_of_materials', 'id (UUID)', 'organization_id, product_id', 'bom_code, revision, is_active, is_approved'],
                ['production_orders', 'id (UUID)', 'organization_id, bom_id', 'order_number, quantity, status, start_date'],
                ['rag_documents', 'id (UUID)', 'organization_id, collection_id', 'title, document_type, storage_path, vector_status'],
                ['ml_models', 'id (UUID)', 'organization_id', 'model_code, algorithm, accuracy_score, stage']
            ],
            [100, 70, 160, 210]
        ),
        ('h2', '3. Indexing & Optimization Strategy'),
        ('body', 'Composite B-Tree indexes are configured on (organization_id, is_deleted, status) across all transaction tables. Vector embedding tables leverage PgVector HNSW (Hierarchical Navigable Small World) indexes with cosine similarity calculation.')
    ]
    create_pdf('DATABASE_SCHEMA.pdf', 'VertexERP AI — Database Schema Specification', 'Data Model Dictionary, ERD References & Indexing Guide', content)

def generate_api_reference_pdf():
    content = [
        ('h2', '1. OpenAPI / REST Gateway Specification'),
        ('body', 'VertexERP AI exposes 75+ RESTful API endpoints adhering to OpenAPI v3 specifications. All endpoints return RFC 7807 structured JSON responses and require Bearer OAuth2 JWT authentication.'),
        ('h2', '2. Router Endpoints Summary Table'),
        ('table',
            ['Endpoint Path', 'Method', 'Module', 'Description'],
            [
                ['/api/v1/auth/login', 'POST', 'Identity', 'Authenticate user and issue JWT bearer token'],
                ['/api/v1/auth/register', 'POST', 'Identity', 'Register new organization tenant and admin user'],
                ['/api/v1/organization', 'GET/POST', 'Organization', 'Retrieve or update tenant metadata and settings'],
                ['/api/v1/employees', 'GET/POST', 'HR Platform', 'List or onboard employees with RBAC check'],
                ['/api/v1/crm/customers', 'GET/POST', 'CRM Platform', 'Manage customer profiles and sales contact lifecycle'],
                ['/api/v1/inventory/products', 'GET/POST', 'Inventory', 'Query product catalog, stock levels, and SKUs'],
                ['/api/v1/finance/invoices', 'GET/POST', 'Finance', 'Create double-entry ledger invoices and payments'],
                ['/api/v1/manufacturing/orders', 'GET/POST', 'Manufacturing', 'Issue shop floor production orders and BOM routes'],
                ['/api/v1/analytics/dashboards/executive', 'GET', 'Analytics', 'Aggregate executive KPI metrics and YoY revenue'],
                ['/api/v1/rag/search', 'POST', 'Enterprise RAG', 'Execute hybrid vector search across uploaded docs'],
                ['/api/v1/copilot/query', 'POST', 'AI Copilot', 'Natural language agent assistant tool execution'],
                ['/api/v1/ml/models', 'GET/POST', 'ML Studio', 'Train, evaluate, and promote machine learning models'],
                ['/api/v1/observability/health', 'GET', 'Monitoring', 'Real-time APM telemetry, Redis & DB health check']
            ],
            [160, 50, 90, 240]
        ),
        ('h2', '3. Common Response Envelope Standard'),
        ('code', '{\n  "success": true,\n  "data": { ... },\n  "message": "Operation completed successfully",\n  "timestamp": "2026-08-01T21:50:00Z"\n}')
    ]
    create_pdf('API_REFERENCE.pdf', 'VertexERP AI — API Reference Manual', 'Complete REST API Endpoint Catalog & Schema Definitions', content)

if __name__ == '__main__':
    generate_system_architecture_pdf()
    generate_database_schema_pdf()
    generate_api_reference_pdf()
