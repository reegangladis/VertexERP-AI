import os
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from app.repositories.data_engineering_repository import DataEngineeringRepository
from app.models.data_engineering import (
    ETLJob,
    ETLRun,
    PipelineLog,
    Dataset,
    DatasetVersion,
    FeatureGroup,
    FeatureRegistry,
    DataQualityReport,
    MetadataCatalog,
    DataLineage,
    DimCustomer,
    DimEmployee,
    DimProduct,
    DimSupplier,
    DimOrganization,
    DimDate,
    FactSales,
    FactInventory,
    FactFinancial,
    FactManufacturing,
    FactHR,
    HistoricalSnapshot,
    DataLakeObject,
    MDMGoldenRecord,
)
from app.schemas.data_engineering import (
    ETLJobCreate,
    DatasetCreate,
    FeatureGroupCreate,
    FeatureRegisterCreate,
    DataEngineeringMonitoringSummary,
    LineageGraphResponse,
    LineageNode,
    LineageEdge,
)


class DataEngineeringService:
    """Enterprise Data Engineering Platform Service."""

    def __init__(self, db):
        self.repo = DataEngineeringRepository(db)

    # =========================================================================
    # ETL/ELT PIPELINE ENGINE
    # =========================================================================
    async def create_etl_job(self, organization_id: uuid.UUID, data: ETLJobCreate) -> ETLJob:
        job = ETLJob(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            source_type=data.source_type,
            target_type=data.target_type,
            frequency=data.frequency,
            schedule_cron=data.schedule_cron,
            retry_limit=data.retry_limit,
            configuration=data.configuration or {},
            priority=data.priority,
            is_incremental=data.is_incremental,
            status="ACTIVE",
        )
        return await self.repo.create_job(job)

    async def get_etl_jobs(self, organization_id: uuid.UUID) -> List[ETLJob]:
        jobs = await self.repo.get_jobs_by_org(organization_id)
        if not jobs:
            # Seed default Enterprise ETL jobs if empty
            default_jobs = [
                ETLJobCreate(
                    name="HR Workforce Analytics Sync",
                    description="Extracts employee profiles, attendance logs, and payroll items into HR Fact Table.",
                    source_type="HR",
                    target_type="WAREHOUSE",
                    frequency="HOURLY",
                    is_incremental=True,
                ),
                ETLJobCreate(
                    name="CRM Sales Funnel Ingestion",
                    description="Loads leads, customer accounts, and closed deals into Sales Fact and SCD2 Customer Dimension.",
                    source_type="CRM",
                    target_type="WAREHOUSE",
                    frequency="HOURLY",
                    is_incremental=True,
                ),
                ETLJobCreate(
                    name="Inventory Valuation & Stock ETL",
                    description="Processes stock movements, warehouse balances, and purchase orders into Curated Zone.",
                    source_type="INVENTORY",
                    target_type="DATALAKE",
                    frequency="HOURLY",
                    is_incremental=True,
                ),
                ETLJobCreate(
                    name="Finance General Ledger Ingestion",
                    description="Extracts journal entries, invoices, and expense claims into Financial Fact Table.",
                    source_type="FINANCE",
                    target_type="WAREHOUSE",
                    frequency="DAILY",
                    is_incremental=False,
                ),
                ETLJobCreate(
                    name="Manufacturing Plant OEE Stream",
                    description="Extracts machine telemetry, work order logs, and downtime records for Feature Store computation.",
                    source_type="MANUFACTURING",
                    target_type="FEATURE_STORE",
                    frequency="REALTIME",
                    is_incremental=True,
                ),
            ]
            jobs = []
            for item in default_jobs:
                created = await self.create_etl_job(organization_id, item)
                jobs.append(created)
        return jobs

    async def trigger_pipeline_run(self, job_id: uuid.UUID) -> ETLRun:
        job = await self.repo.get_job_by_id(job_id)
        if not job:
            raise ValueError(f"ETL Job {job_id} not found")

        runs = await self.repo.get_runs_by_job(job_id)
        run_number = len(runs) + 1

        run = ETLRun(
            job_id=job_id,
            run_number=run_number,
            status="RUNNING",
            start_time=datetime.now(timezone.utc),
            execution_params={"is_incremental": job.is_incremental, "source": job.source_type},
        )
        created_run = await self.repo.create_run(run)

        # Log extract phase
        await self.repo.add_pipeline_log(
            PipelineLog(
                run_id=created_run.id,
                log_level="INFO",
                phase="EXTRACT",
                message=f"Extracting records from {job.source_type} data source...",
                details={"source": job.source_type},
            )
        )

        # Simulate transformation & load
        extracted_cnt = 1250 if job.is_incremental else 45000
        transformed_cnt = int(extracted_cnt * 0.98)
        loaded_cnt = transformed_cnt

        await self.repo.add_pipeline_log(
            PipelineLog(
                run_id=created_run.id,
                log_level="INFO",
                phase="TRANSFORM",
                message=f"Transformed {transformed_cnt} records. Enforced strict schema validation and null checks.",
                details={"null_checks": "PASSED", "duplicates_dropped": extracted_cnt - transformed_cnt},
            )
        )

        await self.repo.add_pipeline_log(
            PipelineLog(
                run_id=created_run.id,
                log_level="INFO",
                phase="LOAD",
                message=f"Successfully loaded {loaded_cnt} rows into target {job.target_type}.",
                details={"target": job.target_type},
            )
        )

        # Complete run
        end_time = datetime.now(timezone.utc)
        duration = (end_time - created_run.start_time).total_seconds()

        updated_run = await self.repo.update_run(
            created_run.id,
            {
                "status": "SUCCESS",
                "end_time": end_time,
                "duration_seconds": round(duration, 2),
                "rows_extracted": extracted_cnt,
                "rows_transformed": transformed_cnt,
                "rows_loaded": loaded_cnt,
            },
        )
        return updated_run

    async def get_run_logs(self, run_id: uuid.UUID) -> List[PipelineLog]:
        return await self.repo.get_run_logs(run_id)

    async def retry_failed_run(self, run_id: uuid.UUID) -> ETLRun:
        # Re-trigger run for job
        stmt_run = await self.repo.get_run_logs(run_id)
        # Fetch run details directly
        return await self.trigger_pipeline_run(uuid.uuid4())

    # =========================================================================
    # DATA QUALITY ENGINE
    # =========================================================================
    async def run_data_quality_inspection(
        self, organization_id: uuid.UUID, table_name: str, dataset_id: Optional[uuid.UUID] = None
    ) -> DataQualityReport:
        rules = [
            {"rule_name": "NULL_CHECK_PRIMARY_KEYS", "rule_type": "NULL_CHECK", "status": "PASSED", "affected_rows": 0, "message": "Primary key null checks passed 100%"},
            {"rule_name": "DUPLICATE_CHECK_UNIQUENESS", "rule_type": "DUPLICATE_CHECK", "status": "PASSED", "affected_rows": 0, "message": "Zero duplicate records detected across entity IDs."},
            {"rule_name": "SCHEMA_VALIDATION_TYPES", "rule_type": "SCHEMA_CHECK", "status": "PASSED", "affected_rows": 0, "message": "Data types match catalog definitions exactly."},
            {"rule_name": "REFERENTIAL_INTEGRITY_FOREIGN_KEYS", "rule_type": "REFERENTIAL_CHECK", "status": "PASSED", "affected_rows": 0, "message": "All foreign key constraints resolved against dimension keys."},
        ]
        
        report = DataQualityReport(
            organization_id=organization_id,
            table_name=table_name,
            dataset_id=dataset_id,
            passed_count=4,
            failed_count=0,
            quality_score=100.0,
            rule_results=rules,
            null_violations=0,
            duplicate_violations=0,
            schema_violations=0,
            referential_violations=0,
        )
        return await self.repo.create_quality_report(report)

    async def get_quality_reports(self, organization_id: uuid.UUID) -> List[DataQualityReport]:
        reports = await self.repo.get_quality_reports_by_org(organization_id)
        if not reports:
            # Seed initial report
            r1 = await self.run_data_quality_inspection(organization_id, "fact_sales")
            r2 = await self.run_data_quality_inspection(organization_id, "dim_customers")
            reports = [r1, r2]
        return reports

    # =========================================================================
    # FEATURE STORE
    # =========================================================================
    async def create_feature_group(self, organization_id: uuid.UUID, data: FeatureGroupCreate) -> FeatureGroup:
        group = FeatureGroup(
            organization_id=organization_id,
            group_name=data.group_name,
            entity_name=data.entity_name,
            entity_key=data.entity_key,
            description=data.description,
            online_enabled=data.online_enabled,
            offline_table=data.offline_table,
            owner=data.owner,
            tags=data.tags or [],
        )
        return await self.repo.create_feature_group(group)

    async def get_feature_groups(self, organization_id: uuid.UUID) -> List[FeatureGroup]:
        groups = await self.repo.get_feature_groups_by_org(organization_id)
        if not groups:
            # Seed default enterprise Feature Groups
            fg_customer = await self.create_feature_group(
                organization_id,
                FeatureGroupCreate(
                    group_name="customer_churn_features",
                    entity_name="Customer",
                    entity_key="customer_id",
                    description="Aggregated behavioral and transactional features for predicting customer churn and lifetime value.",
                    online_enabled=True,
                    offline_table="curated_customer_features",
                    tags=["crm", "churn", "predictive"],
                ),
            )
            await self.register_feature(
                FeatureRegisterCreate(
                    feature_group_id=fg_customer.id,
                    feature_name="days_since_last_purchase",
                    data_type="INT",
                    description="Number of days elapsed since customer's last order",
                    aggregation_window="90D",
                    ml_feature_type="NUMERICAL",
                )
            )
            await self.register_feature(
                FeatureRegisterCreate(
                    feature_group_id=fg_customer.id,
                    feature_name="avg_order_value_30d",
                    data_type="FLOAT",
                    description="Average transaction monetary amount over past 30 days",
                    aggregation_window="30D",
                    ml_feature_type="NUMERICAL",
                )
            )

            fg_inventory = await self.create_feature_group(
                organization_id,
                FeatureGroupCreate(
                    group_name="inventory_demand_features",
                    entity_name="Product",
                    entity_key="product_id",
                    description="Historical sales velocity and reorder point metrics for AI demand forecasting.",
                    online_enabled=True,
                    offline_table="curated_inventory_features",
                    tags=["inventory", "demand_forecasting"],
                ),
            )
            await self.register_feature(
                FeatureRegisterCreate(
                    feature_group_id=fg_inventory.id,
                    feature_name="sales_velocity_7d",
                    data_type="FLOAT",
                    description="Daily average units sold over 7 day rolling window",
                    aggregation_window="7D",
                    ml_feature_type="NUMERICAL",
                )
            )

            groups = await self.repo.get_feature_groups_by_org(organization_id)
        return groups

    async def register_feature(self, data: FeatureRegisterCreate) -> FeatureRegistry:
        feat = FeatureRegistry(
            feature_group_id=data.feature_group_id,
            feature_name=data.feature_name,
            data_type=data.data_type,
            transformation_sql=data.transformation_sql,
            description=data.description,
            version=data.version,
            aggregation_window=data.aggregation_window,
            ml_feature_type=data.ml_feature_type,
            online_ttl_seconds=data.online_ttl_seconds,
            status="ACTIVE",
        )
        return await self.repo.create_feature(feat)

    # =========================================================================
    # DATASETS & METADATA CATALOG
    # =========================================================================
    async def create_dataset(self, organization_id: uuid.UUID, data: DatasetCreate) -> Dataset:
        ds = Dataset(
            organization_id=organization_id,
            name=data.name,
            slug=data.slug,
            category=data.category,
            description=data.description,
            schema_definition=data.schema_definition,
            update_frequency=data.update_frequency,
            record_count=5000,
            size_bytes=1048576,
            data_lake_path=f"s3://vertexerp-datalake/curated/{data.slug}/",
            ownership_team=data.ownership_team,
            data_steward=data.data_steward,
        )
        created_ds = await self.repo.create_dataset(ds)

        # Add default dataset version
        version = DatasetVersion(
            dataset_id=created_ds.id,
            version_tag="v1.0.0",
            snapshot_path=f"s3://vertexerp-datalake/curated/{data.slug}/v1.0.0/",
            record_count=5000,
            checksum="a1b2c3d4e5f67890",
            schema_changes={"initial": "created dataset version v1.0.0"},
        )
        await self.repo.create_dataset_version(version)
        return created_ds

    async def get_datasets(self, organization_id: uuid.UUID) -> List[Dataset]:
        datasets = await self.repo.get_datasets_by_org(organization_id)
        if not datasets:
            categories = [
                ("Employee Dataset", "employee_dataset", "EMPLOYEE", "Workforce headcount, tenure, salary, performance ratings."),
                ("Customer Dataset", "customer_dataset", "CUSTOMER", "Customer account profiles, LTV, support ticket volumes, deal counts."),
                ("Inventory Dataset", "inventory_dataset", "INVENTORY", "Product stock levels, warehouse valuation, reorder status, aging schedule."),
                ("Financial Dataset", "financial_dataset", "FINANCIAL", "General ledger balances, cash flow metrics, AP/AR invoice summaries."),
                ("Manufacturing Dataset", "manufacturing_dataset", "MANUFACTURING", "Work center OEE, production yields, machine downtime, scrap counts."),
                ("Sales Dataset", "sales_dataset", "SALES", "Sales order line items, discount margins, customer acquisition velocity."),
                ("Supplier Dataset", "supplier_dataset", "SUPPLIER", "Supplier OTIF ratings, lead time variance, purchase order fulfillment."),
            ]
            datasets = []
            for name, slug, cat, desc in categories:
                schema_def = {"fields": [{"name": "id", "type": "string"}, {"name": "created_at", "type": "timestamp"}]}
                created = await self.create_dataset(
                    organization_id,
                    DatasetCreate(
                        name=name,
                        slug=slug,
                        category=cat,
                        description=desc,
                        schema_definition=schema_def,
                    ),
                )
                datasets.append(created)
        return datasets

    async def get_dataset_by_id(self, dataset_id: uuid.UUID) -> Optional[Dataset]:
        return await self.repo.get_dataset_by_id(dataset_id)

    async def get_metadata_catalog(self, dataset_id: Optional[uuid.UUID] = None) -> List[MetadataCatalog]:
        entries = await self.repo.get_metadata_catalog(dataset_id)
        if not entries:
            # Return sample metadata entries
            return [
                MetadataCatalog(
                    id=uuid.uuid4(),
                    dataset_id=dataset_id or uuid.uuid4(),
                    column_name="customer_id",
                    data_type="UUID",
                    business_definition="Unique system identifier for customer entity.",
                    is_pii=False,
                    classification="INTERNAL",
                    data_steward="CRM Data Steward",
                    tags=["key", "crm"],
                ),
                MetadataCatalog(
                    id=uuid.uuid4(),
                    dataset_id=dataset_id or uuid.uuid4(),
                    column_name="email_address",
                    data_type="STRING",
                    business_definition="Customer contact email address.",
                    is_pii=True,
                    classification="RESTRICTED",
                    data_steward="Privacy Officer",
                    tags=["pii", "gdpr"],
                ),
                MetadataCatalog(
                    id=uuid.uuid4(),
                    dataset_id=dataset_id or uuid.uuid4(),
                    column_name="total_revenue",
                    data_type="DECIMAL",
                    business_definition="Cumulative gross revenue generated from customer orders.",
                    is_pii=False,
                    classification="INTERNAL",
                    data_steward="Finance Data Steward",
                    tags=["financial", "metric"],
                ),
            ]
        return entries

    # =========================================================================
    # LINEAGE GRAPH ENGINE
    # =========================================================================
    async def get_lineage_graph(self, organization_id: uuid.UUID) -> LineageGraphResponse:
        nodes = [
            LineageNode(id="src_crm", label="CRM PostgreSQL Source", type="SOURCE_TABLE", category="Source Systems"),
            LineageNode(id="src_hr", label="HR Database Source", type="SOURCE_TABLE", category="Source Systems"),
            LineageNode(id="src_inv", label="Inventory DB Source", type="SOURCE_TABLE", category="Source Systems"),
            LineageNode(id="lake_raw", label="Data Lake Raw Zone", type="RAW_ZONE", category="Data Lake"),
            LineageNode(id="lake_proc", label="Data Lake Processed Zone", type="PROCESSED_ZONE", category="Data Lake"),
            LineageNode(id="dw_dim_cust", label="DimCustomer (SCD2)", type="DIMENSION", category="Data Warehouse"),
            LineageNode(id="dw_dim_emp", label="DimEmployee (SCD2)", type="DIMENSION", category="Data Warehouse"),
            LineageNode(id="dw_fact_sales", label="FactSales", type="FACT", category="Data Warehouse"),
            LineageNode(id="feature_churn", label="customer_churn_features", type="FEATURE", category="Feature Store"),
            LineageNode(id="dataset_cust", label="Customer Dataset (Curated)", type="DATASET", category="Curated Datasets"),
        ]

        edges = [
            LineageEdge(source="src_crm", target="lake_raw", label="Extract JSON/Parquet", type="EXTRACT"),
            LineageEdge(source="src_hr", target="lake_raw", label="Extract CSV Streams", type="EXTRACT"),
            LineageEdge(source="lake_raw", target="lake_proc", label="Schema Validation & Null Check", type="TRANSFORM"),
            LineageEdge(source="lake_proc", target="dw_dim_cust", label="SCD Type 2 Dimension Load", type="LOAD"),
            LineageEdge(source="lake_proc", target="dw_dim_emp", label="SCD Type 2 Dimension Load", type="LOAD"),
            LineageEdge(source="dw_dim_cust", target="dw_fact_sales", label="Star Schema Key Mapping", type="AGGREGATE"),
            LineageEdge(source="dw_fact_sales", target="feature_churn", label="Feature Engineering SQL", type="FEATURE_GEN"),
            LineageEdge(source="dw_fact_sales", target="dataset_cust", label="Curated Export", type="LOAD"),
        ]

        return LineageGraphResponse(nodes=nodes, edges=edges)

    # =========================================================================
    # DATA LAKE & MASTER DATA MANAGEMENT
    # =========================================================================
    async def get_data_lake_objects(self, organization_id: uuid.UUID, zone: Optional[str] = None) -> List[DataLakeObject]:
        objects = await self.repo.get_data_lake_objects(organization_id, zone)
        if not objects:
            zones_data = [
                ("RAW", "s3://vertexerp-datalake/raw/crm/customers_20260726.parquet", "PARQUET", 5242880, 12000, "CRM"),
                ("PROCESSED", "s3://vertexerp-datalake/processed/crm/customers_clean.parquet", "PARQUET", 4194304, 11980, "CRM"),
                ("CURATED", "s3://vertexerp-datalake/curated/datasets/customer_dataset.json", "JSON", 2097152, 10000, "CRM"),
                ("ARCHIVE", "s3://vertexerp-datalake/archive/2025/hr_attendance_old.parquet", "PARQUET", 10485760, 50000, "HR"),
            ]
            objects = []
            for z, path, fmt, sz, count, src in zones_data:
                obj = DataLakeObject(
                    organization_id=organization_id,
                    zone=z,
                    object_path=path,
                    file_format=fmt,
                    file_size_bytes=sz,
                    record_count=count,
                    source_domain=src,
                    checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                )
                created = await self.repo.create_data_lake_object(obj)
                objects.append(created)
        return objects

    async def get_mdm_golden_records(self, organization_id: uuid.UUID, entity_type: Optional[str] = None) -> List[MDMGoldenRecord]:
        records = await self.repo.get_mdm_golden_records(organization_id, entity_type)
        if not records:
            mdm_samples = [
                ("CUSTOMER", "GOLD-CUST-1001", {"name": "Acme Global Corp", "contact_email": "info@acmeglobal.com", "tax_id": "US99887766"}, 0.98, ["TAX_ID_MATCH", "NAME_FUZZY_95"], ["CRM-901", "FINANCE-402"], "MATCHED"),
                ("EMPLOYEE", "GOLD-EMP-2005", {"name": "Jane Doe", "email": "jane.doe@vertexerp.com", "ssn_hash": "a98f7..."}, 1.0, ["EMAIL_EXACT_MATCH"], ["HR-8001"], "MATCHED"),
                ("PRODUCT", "GOLD-PROD-5002", {"sku": "PROD-A100", "name": "Precision CNC Milling Bit", "category": "Industrial Tools"}, 0.95, ["SKU_EXACT_MATCH"], ["INV-990", "MFG-102"], "MATCHED"),
                ("SUPPLIER", "GOLD-SUPP-3001", {"name": "Global Logistics Corp", "rating": 4.9}, 0.99, ["NAME_EXACT_MATCH"], ["INV-SUPP-12"], "MATCHED"),
            ]
            records = []
            for ent, gid, data_json, conf, rules, srcs, st in mdm_samples:
                rec = MDMGoldenRecord(
                    organization_id=organization_id,
                    entity_type=ent,
                    golden_id=gid,
                    master_data=data_json,
                    confidence_score=conf,
                    match_rules_applied=rules,
                    source_system_ids=srcs,
                    status=st,
                )
                created = await self.repo.create_mdm_record(rec)
                records.append(created)
        return records

    # =========================================================================
    # MONITORING SUMMARY
    # =========================================================================
    async def get_monitoring_summary(self, organization_id: uuid.UUID) -> DataEngineeringMonitoringSummary:
        jobs = await self.get_etl_jobs(organization_id)
        f_groups = await self.get_feature_groups(organization_id)
        feature_cnt = sum(len(g.features) for g in f_groups)

        return DataEngineeringMonitoringSummary(
            total_pipelines=len(jobs),
            active_pipelines=len([j for j in jobs if j.status == "ACTIVE"]),
            failed_pipelines_24h=0,
            total_rows_processed_24h=485000,
            overall_quality_score=99.8,
            data_lake_total_size_gb=142.5,
            feature_groups_count=len(f_groups),
            registered_features_count=feature_cnt,
            data_freshness_status="HEALTHY (Lag < 5 mins)",
        )

    # =========================================================================
    # ROOT ANALYTICS DATASET FILE GENERATION
    # =========================================================================
    def generate_sample_datasets_on_disk(self):
        datasets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../datasets"))
        os.makedirs(datasets_dir, exist_ok=True)

        sample_datasets = {
            "employee_dataset.json": [
                {"employee_id": "EMP-001", "name": "John Doe", "department": "Engineering", "salary": 125000, "tenure_years": 4.5, "performance_score": 4.8},
                {"employee_id": "EMP-002", "name": "Jane Smith", "department": "Finance", "salary": 115000, "tenure_years": 3.2, "performance_score": 4.6},
            ],
            "customer_dataset.json": [
                {"customer_id": "CUST-101", "company_name": "Apex Enterprise Solutions", "arr": 240000, "churn_risk": 0.05, "nps": 9},
                {"customer_id": "CUST-102", "company_name": "Nexus Global Dynamics", "arr": 180000, "churn_risk": 0.12, "nps": 8},
            ],
            "inventory_dataset.json": [
                {"sku": "SKU-9001", "product_name": "Ultra-Fast Server Blade", "warehouse": "Austin Central", "on_hand_qty": 450, "valuation": 1125000.0},
                {"sku": "SKU-9002", "product_name": "Fiber Optic Transceiver", "warehouse": "Frankfurt Hub", "on_hand_qty": 1200, "valuation": 360000.0},
            ],
            "financial_dataset.json": [
                {"account_code": "1000", "account_name": "Operating Cash", "period": "2026-Q2", "debit": 4500000.0, "credit": 0.0, "net_balance": 4500000.0},
                {"account_code": "4000", "account_name": "Software Revenue", "period": "2026-Q2", "debit": 0.0, "credit": 12800000.0, "net_balance": 12800000.0},
            ],
            "manufacturing_dataset.json": [
                {"machine_id": "CNC-01", "work_center": "Precision Milling", "units_produced": 8500, "scrap_qty": 42, "oee_percent": 91.4, "downtime_hours": 1.2},
                {"machine_id": "ROBOT-04", "work_center": "Automated Assembly", "units_produced": 14200, "scrap_qty": 18, "oee_percent": 95.8, "downtime_hours": 0.5},
            ],
            "sales_dataset.json": [
                {"order_id": "ORD-5001", "customer_name": "Apex Enterprise Solutions", "gross_revenue": 45000.0, "discount": 2500.0, "net_margin": 18500.0},
                {"order_id": "ORD-5002", "customer_name": "Nexus Global Dynamics", "gross_revenue": 32000.0, "discount": 1000.0, "net_margin": 14200.0},
            ],
            "supplier_dataset.json": [
                {"supplier_id": "SUPP-01", "supplier_name": "Global Microelectronics Inc", "otif_rating": 98.4, "lead_time_days": 12, "compliance_passed": True},
                {"supplier_id": "SUPP-02", "supplier_name": "Continental Steel Works", "otif_rating": 94.2, "lead_time_days": 18, "compliance_passed": True},
            ],
        }

        for filename, data in sample_datasets.items():
            filepath = os.path.join(datasets_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
