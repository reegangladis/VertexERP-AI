# Database Schema Documentation (Phase 4)

This document provides detail on the relational SQL schema and database models introduced for **Phase 4 - HR Intelligence Platform**.

---

## 1. Schema Diagram Overview

The following entity tables model organization settings, geographic branches, hierarchical departments, teams, designation tiers, public calendars, and policy documents:

```
[organizations]
       │
       ├─── [branches] (Self-referencing parent_branch_id)
       │       │
       │       └─── [departments] (Self-referencing parent_department_id)
       │               │
       │               └─── [teams] (Self-referencing parent_team_id)
       │
       ├─── [locations] (Offices, Warehouses)
       │
       ├─── [designations] (Job grades, hierarchy ordering scale)
       │
       ├─── [business_calendars] ─── [working_days] & [holidays]
       │
       └─── [organization_documents] & [organization_metadata]
```

HR Platforms models:
```
[employees] ─── [employee_profiles]
   │
   ├─── [attendance] (Punch card check in/out)
   ├─── [leave_balances] & [leave_requests]
   ├─── [salary_structures] (Payroll configurations)
   ├─── [goals] & [performance_reviews]
   ├─── [training_records]
   └─── [employee_documents] & [employee_notes]
```

---

## 2. Table Specifications

### 2.1. `branches`
Represents physical or operational branch structures of the organization.
*   `id`: UUID (Primary Key, unique)
*   `organization_id`: UUID (Foreign Key -> `organizations.id`, index)
*   `name`: VARCHAR(255) (Not Null)
*   `slug`: VARCHAR(255) (Unique per org)
*   `code`: VARCHAR(50) (Nullable)
*   `timezone`: VARCHAR(100) (Default 'UTC')
*   `address_line1`: VARCHAR(255)
*   `city`: VARCHAR(100)
*   `country`: VARCHAR(100)
*   `parent_branch_id`: UUID (Foreign Key -> `branches.id`, self-referential parent)
*   `manager_id`: UUID (Foreign Key -> `users.id`, nullable)
*   `is_active`: BOOLEAN (Default True)
*   `is_deleted`: BOOLEAN (Default False)

### 2.2. `departments`
*   `id`: UUID (Primary Key)
*   `organization_id`: UUID (Foreign Key -> `organizations.id`)
*   `branch_id`: UUID (Foreign Key -> `branches.id`, nullable)
*   `name`: VARCHAR(255)
*   `slug`: VARCHAR(255)
*   `code`: VARCHAR(50)
*   `budget`: DECIMAL(15, 2) (Default 0.00)
*   `parent_department_id`: UUID (Foreign Key -> `departments.id`, self-referential)
*   `status`: VARCHAR(50) (Default 'active')

### 2.3. `teams`
*   `id`: UUID (Primary Key)
*   `organization_id`: UUID (Foreign Key)
*   `department_id`: UUID (Foreign Key -> `departments.id`)
*   `name`: VARCHAR(255)
*   `slug`: VARCHAR(255)
*   `description`: TEXT
*   `parent_team_id`: UUID (Foreign Key -> `teams.id`, self-referential)
*   `status`: VARCHAR(50)

### 2.4. `designations`
Defines job titles, reporting grades, and hierarchy levels.
*   `id`: UUID (Primary Key)
*   `organization_id`: UUID (Foreign Key)
*   `name`: VARCHAR(255)
*   `slug`: VARCHAR(255)
*   `title`: VARCHAR(255)
*   `code`: VARCHAR(50)
*   `job_level`: VARCHAR(100) (e.g. 'Executive', 'Senior')
*   `grade`: VARCHAR(50) (e.g. 'G1', 'L5')
*   `reporting_level`: INTEGER (Default 1)

### 2.5. `locations`
*   `id`: UUID
*   `organization_id`: UUID
*   `name`: VARCHAR(255)
*   `type`: VARCHAR(50) (e.g. `office`, `remote`, `warehouse`)
*   `address_line1`: VARCHAR(255)
*   `city`: VARCHAR(100)
*   `state`: VARCHAR(100)
*   `country`: VARCHAR(100)
*   `postal_code`: VARCHAR(20)

### 2.6. `business_calendars`
*   `id`: UUID
*   `organization_id`: UUID
*   `name`: VARCHAR(255)
*   `year`: INTEGER
*   `is_active`: BOOLEAN

### 2.7. `working_days`
*   `id`: UUID
*   `calendar_id`: UUID (Foreign Key -> `business_calendars.id`)
*   `day_of_week`: INTEGER (0 = Monday, 6 = Sunday)
*   `is_working`: BOOLEAN (Default True)
*   `start_time`: VARCHAR(10) (e.g. '09:00')
*   `end_time`: VARCHAR(10) (e.g. '18:00')

### 2.8. `holidays`
*   `id`: UUID
*   `calendar_id`: UUID (Foreign Key -> `business_calendars.id`)
*   `name`: VARCHAR(255)
*   `date`: DATE
*   `type`: VARCHAR(50) (e.g. `public`, `company`)

### 2.9. `organization_documents`
*   `id`: UUID
*   `organization_id`: UUID
*   `name`: VARCHAR(255)
*   `type`: VARCHAR(100) (e.g. `handbook`, `policy`, `license`)
*   `file_path`: VARCHAR(512)
*   `file_size`: INTEGER
*   `mime_type`: VARCHAR(100)
*   `storage_provider`: VARCHAR(50) (e.g. `local`, `s3`, `azure`)
*   `metadata_json`: JSONB

---

## 3. User Extensions
To bind employees to designations and hierarchy reporting structures, the following columns were added to the `users` table:
*   `manager_id`: UUID (Foreign Key -> `users.id`, self-referential reporting line)
*   `designation_id`: UUID (Foreign Key -> `designations.id`)

---

## 4. HR Platform Tables (Phase 4)

### 4.1. `employees`
*   `id`: UUID (Primary Key)
*   `organization_id`: UUID (Foreign Key -> `organizations.id`)
*   `user_id`: UUID (Foreign Key -> `users.id`, unique)
*   `employee_code`: VARCHAR(100) (Not Null)
*   `employment_type`: VARCHAR(50) (Default 'full-time')
*   `status`: VARCHAR(50) (Default 'active')
*   `date_joined`: DATE (Not Null)
*   `date_terminated`: DATE
*   `branch_id`: UUID
*   `department_id`: UUID
*   `designation_id`: UUID
*   `manager_id`: UUID (Foreign Key -> `employees.id`, self-referencing manager)

### 4.2. `employee_profiles`
*   `id`: UUID (Primary Key)
*   `employee_id`: UUID (Foreign Key -> `employees.id`, unique)
*   `personal_email`: VARCHAR(255)
*   `personal_phone`: VARCHAR(50)
*   `date_of_birth`: DATE
*   `gender`: VARCHAR(50)
*   `emergency_contacts`: JSONB (List of emergency contact profiles)
*   `photo_url`: VARCHAR(512)

### 4.3. `attendance`
*   `id`: UUID
*   `employee_id`: UUID (Foreign Key -> `employees.id`)
*   `date`: DATE (Not Null)
*   `check_in`: DATETIME
*   `check_out`: DATETIME
*   `total_hours`: DECIMAL(5,2)
*   `is_late_arrival`: BOOLEAN (Default False)
*   `is_early_exit`: BOOLEAN (Default False)
*   `overtime_minutes`: INTEGER (Default 0)

### 4.4. `leave_types`
*   `id`: UUID
*   `organization_id`: UUID
*   `name`: VARCHAR(255)
*   `code`: VARCHAR(50)
*   `days_per_year`: DECIMAL(5,2)
*   `is_carry_forward`: BOOLEAN

### 4.5. `leave_balances`
*   `id`: UUID
*   `employee_id`: UUID
*   `leave_type_id`: UUID
*   `year`: INTEGER
*   `allocated`: DECIMAL(5,2)
*   `used`: DECIMAL(5,2)
*   `remaining`: DECIMAL(5,2)

### 4.6. `leave_requests`
*   `id`: UUID
*   `employee_id`: UUID
*   `leave_type_id`: UUID
*   `start_date`: DATE
*   `end_date`: DATE
*   `total_days`: DECIMAL(5,2)
*   `status`: VARCHAR(50) (Default 'pending')
*   `approved_by_id`: UUID (Foreign Key -> `employees.id`)

### 4.7. `salary_structures`
*   `id`: UUID
*   `employee_id`: UUID
*   `base_salary`: DECIMAL(15,2)
*   `allowances`: JSONB
*   `deductions`: JSONB
*   `benefits`: JSONB
*   `effective_from`: DATE
*   `effective_to`: DATE

---

## 5. CRM Platform Tables (Phase 5)

### 5.1. `lead_sources`
*   `id`: UUID (Primary Key)
*   `organization_id`: UUID
*   `name`: VARCHAR(255)
*   `code`: VARCHAR(50)

### 5.2. `leads`
*   `id`: UUID
*   `organization_id`: UUID
*   `first_name`: VARCHAR(255)
*   `last_name`: VARCHAR(255)
*   `email`: VARCHAR(255)
*   `phone`: VARCHAR(50)
*   `company`: VARCHAR(255)
*   `status`: VARCHAR(50)
*   `lead_source_id`: UUID (Foreign Key -> `lead_sources.id`)
*   `score`: INTEGER
*   `assigned_to_id`: UUID (Foreign Key -> `users.id`)

### 5.3. `lead_activities`
*   `id`: UUID
*   `lead_id`: UUID (Foreign Key -> `leads.id`)
*   `type`: VARCHAR(50)
*   `title`: VARCHAR(255)
*   `description`: VARCHAR(1000)

### 5.4. `customers`
*   `id`: UUID
*   `organization_id`: UUID
*   `type`: VARCHAR(50)
*   `name`: VARCHAR(255)
*   `industry`: VARCHAR(100)
*   `status`: VARCHAR(50)
*   `communication_preferences`: JSONB
*   `tags`: JSONB

### 5.5. `contacts`
*   `id`: UUID
*   `organization_id`: UUID
*   `customer_id`: UUID (Foreign Key -> `customers.id`)
*   `first_name`: VARCHAR(255)
*   `last_name`: VARCHAR(255)
*   `email`: VARCHAR(255)
*   `phone`: VARCHAR(50)
*   `job_title`: VARCHAR(100)
*   `department`: VARCHAR(100)
*   `social_links`: JSONB
*   `is_primary`: BOOLEAN

### 5.6. `opportunities`
*   `id`: UUID
*   `organization_id`: UUID
*   `title`: VARCHAR(255)
*   `description`: VARCHAR(2000)
*   `stage`: VARCHAR(100)
*   `close_date`: DATE

### 5.7. `deals`
*   `id`: UUID
*   `organization_id`: UUID
*   `opportunity_id`: UUID (Foreign Key -> `opportunities.id`)
*   `customer_id`: UUID (Foreign Key -> `customers.id`)
*   `title`: VARCHAR(255)
*   `amount`: DECIMAL(15,2)
*   `probability`: INTEGER
*   `status`: VARCHAR(50)
*   `won_lost_reason`: VARCHAR(1000)

### 5.8. `quotations`
*   `id`: UUID
*   `deal_id`: UUID (Foreign Key -> `deals.id`)
*   `version`: INTEGER
*   `status`: VARCHAR(50)
*   `terms`: VARCHAR(2000)
*   `valid_until`: DATE
*   `file_path`: VARCHAR(512)

### 5.9. `crm_tasks`
*   `id`: UUID
*   `organization_id`: UUID
*   `customer_id`: UUID
*   `lead_id`: UUID
*   `title`: VARCHAR(255)
*   `description`: VARCHAR(1000)
*   `due_date`: DATE
*   `priority`: VARCHAR(50)
*   `status`: VARCHAR(50)
*   `assigned_to_id`: UUID

### 5.10. `meetings`
*   `id`: UUID
*   `organization_id`: UUID
*   `customer_id`: UUID
*   `lead_id`: UUID
*   `title`: VARCHAR(255)
*   `scheduled_at`: DATETIME
*   `duration_minutes`: INTEGER
*   `location_or_url`: VARCHAR(255)

### 5.11. `support_tickets`
*   `id`: UUID
*   `organization_id`: UUID
*   `customer_id`: UUID
*   `category`: VARCHAR(100)
*   `priority`: VARCHAR(50)
*   `status`: VARCHAR(50)
*   `assigned_to_id`: UUID
*   `resolution_notes`: VARCHAR(2000)

### 5.12. `campaigns`
*   `id`: UUID
*   `organization_id`: UUID
*   `name`: VARCHAR(255)
*   `type`: VARCHAR(100)
*   `status`: VARCHAR(50)
*   `start_date`: DATE
*   `end_date`: DATE
*   `budget`: DECIMAL(15,2)
*   `expected_revenue`: DECIMAL(15,2)

---

## 6. Enterprise Data Engineering Platform Tables (Phase 10)

### 6.1. Core Pipelines & Infrastructure
*   `etl_jobs`: Job definitions (`name`, `source_type`, `target_type`, `frequency`, `schedule_cron`, `status`, `retry_limit`, `configuration`, `priority`, `is_incremental`)
*   `etl_runs`: Execution runs (`job_id`, `run_number`, `status`, `start_time`, `end_time`, `duration_seconds`, `rows_extracted`, `rows_transformed`, `rows_loaded`)
*   `pipeline_logs`: Log events (`run_id`, `timestamp`, `log_level`, `phase`, `message`, `details`)

### 6.2. Data Warehouse (Star & Snowflake Schema with SCD Type 2)
*   `dim_customers`, `dim_employees`, `dim_products`, `dim_suppliers`, `dim_organizations`: SCD Type 2 dimensions (`effective_date`, `expiration_date`, `is_current`, `version`)
*   `dim_dates`: Time dimension (`date_key`, `full_date`, `year`, `quarter`, `month`, `day_of_week`, `is_weekend`)
*   `fact_sales`, `fact_inventory`, `fact_financials`, `fact_manufacturing`, `fact_hr`: Fact tables
*   `historical_snapshots`: Point-in-time warehouse checksum audit snapshots

### 6.3. Data Lake, MDM, Catalog & Feature Store
*   `data_lake_objects`: Data Lake storage zone objects (`zone`, `object_path`, `file_format`, `file_size_bytes`, `record_count`)
*   `mdm_golden_records`: Master Data Management golden records (`entity_type`, `golden_id`, `master_data`, `confidence_score`, `match_rules_applied`)
*   `datasets` & `dataset_versions`: Analytics dataset catalog & version snapshots
*   `metadata_catalog`: Business dictionary & PII column definitions (`column_name`, `data_type`, `business_definition`, `is_pii`, `data_steward`)
*   `feature_groups` & `feature_registry`: AI Feature Store groups, features, and vector flags
*   `data_quality_reports`: Validation rules & quality scores
*   `data_lineage`: Pipeline and dataset DAG lineage edges

---

## 7. Enterprise RAG Platform Tables (Phase 13)

### 7.1. Relational Content & Vector Mapping
*   `knowledge_collections`: Logical directories grouping documents (`organization_id`, `name`, `slug`, `description`, `category`, `tags`, `is_public`, `metadata_json`, `created_by`)
*   `documents`: Ingested document records (`organization_id`, `collection_id`, `title`, `file_name`, `file_path`, `file_size`, `mime_type`, `document_type`, `format`, `language`, `category`, `tags`, `current_version`, `status`, `approval_status`, `retention_days`, `metadata_json`, `created_by`, `updated_by`)
*   `document_versions`: Document history version records (`document_id`, `version_number`, `file_path`, `file_size`, `file_hash`, `change_summary`, `metadata_json`, `created_by`)
*   `document_chunks`: Extracted semantic text segments (`document_id`, `version_id`, `chunk_index`, `content`, `clean_content`, `token_count`, `word_count`, `chunk_hash`, `language`, `metadata_json`)
*   `embeddings_metadata`: Vector DB references (`chunk_id`, `provider`, `model_name`, `vector_id`, `dimension`, `status`, `metadata_json`)

### 7.2. Chat Telemetry & Auditing Logs
*   `chat_sessions`: Persistent RAG chatbot conversations (`organization_id`, `user_id`, `title`, `is_pinned`, `context_metadata`)
*   `chat_messages`: Question & Answer histories (`session_id`, `role`, `content`, `prompt_tokens`, `completion_tokens`, `citations`, `feedback_rating`, `feedback_text`)
*   `retrieval_logs`: Full-text logs auditing retrieval execution (`organization_id`, `session_id`, `user_id`, `query_text`, `top_k`, `retrieved_chunk_ids`, `scores`, `execution_time_ms`, `search_type`)
*   `feedback`: User accuracy reports mapping chunks (`organization_id`, `user_id`, `chat_message_id`, `chunk_id`, `rating`, `feedback_type`, `comments`, `metadata_json`)

---

## 8. Enterprise AI Copilot Platform Tables (Phase 14)

### 8.1. Sessions & Messages
*   `copilot_sessions`: Multi-tenant session identifiers (`organization_id`, `user_id`, `title`, `is_pinned`, `context_metadata`, `created_at`, `updated_at`)
*   `copilot_messages`: Timelines logs (`session_id`, `role`, `content`, `prompt_tokens`, `completion_tokens`, `latency_ms`, `tool_calls` (JSON), `citations` (JSON), `generated_from` (Prompt version), `created_at`)

### 8.2. Prompt Templates & Registry
*   `copilot_prompts`: Customizable prompt templates database (`organization_id`, `name`, `type` [system/department], `department`, `template`, `variables` (JSON), `version`, `is_active`, `created_by`, `created_at`, `updated_at`)
*   `tool_registry`: Backend operation interfaces catalog (`name`, `description`, `parameters_schema` (JSON), `required_role`, `is_active`, `created_at`, `updated_at`)

### 8.3. Executions & Feedback
*   `tool_executions`: Trace details of tool runs (`message_id`, `tool_name`, `arguments` (JSON), `result` (JSON), `status` [success/failed], `error_message`, `execution_time_ms`, `created_at`)
*   `conversation_feedback`: Ratings audit reports (`message_id`, `user_id`, `rating` [1-5], `comment`, `created_at`)
*   `conversation_metadata`: Session key-value mappings (`session_id`, `meta_key`, `meta_value`, `created_at`)



