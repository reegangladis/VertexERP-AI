# Organization Management API Documentation

This document describes the REST API endpoints implemented under Phase 3 - Organization Management Platform. All endpoints return standardized `APIResponse` payloads.

---

## 1. Branch Registry

### `GET /api/v1/branches`
Retrieve a paginated, searchable, sorted list of organization branches.
*   **Query Parameters**:
    *   `skip` (int, default=0): Number of records to skip.
    *   `limit` (int, default=100): Maximum records to return.
    *   `search` (str, optional): Filters branches by name, slug, or code.
    *   `sort` (str, optional): Sorting field (prefix with `-` for descending, e.g. `-name`).
*   **Response**:
    ```json
    {
      "success": true,
      "message": "Branches retrieved successfully",
      "data": [
        {
          "id": "893c52a0-4ff6-4fa2-bf6d-88b1fb2fa00b",
          "name": "Boston Office",
          "slug": "boston-office",
          "code": "BOS-01",
          "timezone": "America/New_York",
          "city": "Boston",
          "country": "USA",
          "parent_branch_id": null
        }
      ]
    }
    ```

### `POST /api/v1/branches`
Create a new branch subdivision.
*   **Request Payload**:
    ```json
    {
      "name": "Dublin Hub",
      "slug": "dublin-hub",
      "code": "DUB-02",
      "timezone": "GMT",
      "city": "Dublin",
      "country": "Ireland"
    }
    ```

### `PUT /api/v1/branches/{id}`
Update branch details.

### `DELETE /api/v1/branches/{id}`
Soft-delete a branch register.

---

## 2. Department Administration

### `GET /api/v1/departments`
Retrieve departments with details including associated budgets and branches.

### `POST /api/v1/departments`
Create a new department.
*   **Request Payload**:
    ```json
    {
      "name": "Engineering Operations",
      "slug": "engineering-ops",
      "code": "ENG-OPS",
      "budget": 2500000.0,
      "branch_id": "893c52a0-4ff6-4fa2-bf6d-88b1fb2fa00b"
    }
    ```

---

## 3. Team Management

### `GET /api/v1/teams`
Retrieve list of teams and sub-teams.

### `POST /api/v1/teams`
Create a new team under a department.

---

## 4. Designations & Job Levels

### `GET /api/v1/designations`
Get roles, designations, titles, grades, and hierarchy levels.

### `POST /api/v1/designations`
Configure a designation title.

---

## 5. Location Directory

### `GET /api/v1/locations`
List physical, remote, and warehouse locations.

### `POST /api/v1/locations`
Create physical point coordinates.

---

## 6. Business Calendar

### `GET /api/v1/business-calendar`
List active fiscal calendars.

### `GET /api/v1/business-calendar/{id}/working-days`
Get working days list (0-6) and shift timings.

### `POST /api/v1/business-calendar/{id}/working-days`
Update active working day configurations.

### `POST /api/v1/business-calendar/{id}/holidays`
Add public or company holidays.

---

## 7. Reporting & Hierarchy Tree

### `GET /api/v1/reporting-structure/tree`
Generates a recursive list structure showing employee reporting mappings starting from the CEO.
*   **Response**:
    ```json
    {
      "success": true,
      "message": "Reporting tree generated",
      "data": [
        {
          "user": {
            "id": "1a2b3c4d-...",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "ceo@vertexerp.ai",
            "designation_title": "Chief Executive Officer",
            "job_level": "L10",
            "reporting_level": 1
          },
          "subordinates": [
            {
              "user": {
                "first_name": "Bob",
                "last_name": "Jones",
                "designation_title": "VP of Engineering"
              },
              "subordinates": []
            }
          ]
        }
      ]
    }
    ```

---

## 8. Policy Document Uploads

### `POST /api/v1/documents/upload`
Upload a corporate handbook or policy document.
*   **Content-Type**: `multipart/form-data`
*   **Parameters**:
    *   `name` (str): File name representation.
    *   `type` (str): e.g. `handbook`, `policy`, `license`.
    *   `provider` (str): `local` or cloud providers.
    *   `file` (binary): The file to upload.

### `GET /api/v1/documents/{id}/download`
Download the document file stream.

---

## 9. HR Intelligence & Employee Lifecycle APIs (Phase 4)

### `GET /api/v1/employees`
Retrieve a paginated, searchable, filtered list of employees.
*   **Query Parameters**:
    *   `skip` (int): Offset records.
    *   `limit` (int): Number of records.
    *   `search` (str): Search by employee code, name, phone, or email.

### `POST /api/v1/employees`
Create a new employee profile.

### `POST /api/v1/employees/bulk-upload`
Upload a CSV file containing bulk employee records.
*   **Content-Type**: `multipart/form-data`

### `GET /api/v1/employees/export/csv`
Download employee directory as a CSV file.

### `POST /api/v1/attendance/check-in`
Check in active employee shift.

### `POST /api/v1/attendance/check-out`
Check out active employee shift.

### `GET /api/v1/leaves/requests`
List submitted leave requests.

### `POST /api/v1/leaves/requests`
File a new leave request. Balances are checked before creation.

### `PUT /api/v1/leaves/requests/{id}/approval`
Approve or reject a pending leave request. Balances deduct on approval.

### `GET /api/v1/recruitment/jobs`
List published job openings.

### `POST /api/v1/recruitment/jobs`
Publish a new job position opening.

### `GET /api/v1/performance/goals`
List assigned target goals and completion percentages.

### `GET /api/v1/training/courses`
List certification training courses.

### `POST /api/v1/payroll/salary-structures`
Configure employee base salary structure.

---

## 10. CRM Intelligence & Sales Staging APIs (Phase 5)

### `GET /api/v1/crm/leads`
Retrieve a paginated, searchable, filtered list of leads.
*   **Query Parameters**:
    *   `skip` (int): Offset records.
    *   `limit` (int): Number of records.
    *   `search` (str): Search by name, email, company.

### `POST /api/v1/crm/leads`
Create a new lead profile. Deduplication checks are run, and AI Lead Scoring is calculated based on channel code.

### `POST /api/v1/crm/leads/bulk-upload`
Upload a CSV file containing bulk lead records.
*   **Content-Type**: `multipart/form-data`

### `GET /api/v1/crm/leads/export/csv`
Download leads directory as a CSV file.

### `GET /api/v1/crm/customers`
Retrieve customer accounts.

### `POST /api/v1/crm/customers`
Create a customer profile (optionally binding a contacts list).

### `POST /api/v1/crm/customers/bulk-upload`
Bulk upload customers from a CSV file.

### `GET /api/v1/crm/customers/export/csv`
Export customer registry as a CSV file.

### `GET /api/v1/crm/contacts`
List contact details.

### `GET /api/v1/crm/deals/opportunities`
List opportunities stages.

### `GET /api/v1/crm/deals`
List deal amounts, close probability ratings, and status.

### `POST /api/v1/crm/deals`
Create a new deal contract in the pipeline.

### `PUT /api/v1/crm/deals/{id}/result`
Process a deal as won or lost, logging reasons and probability updates.

### `GET /api/v1/crm/activities/tasks`
List assigned task trackers.

### `GET /api/v1/crm/activities/meetings`
List scheduled meetings.

### `GET /api/v1/crm/support-tickets`
List customer support cases.

### `POST /api/v1/crm/support-tickets`
File a support ticket category.

### `PUT /api/v1/crm/support-tickets/{id}`
Update support ticket status to resolved and record resolution notes.

### `GET /api/v1/crm/campaigns`
List marketing campaigns, budgets, and expected revenues.

### `POST /api/v1/crm/campaigns`
Launch a new marketing campaign.

---

## 11. Data Engineering Platform APIs (Phase 10)

### `GET /api/v1/data-engineering/etl-jobs`
List all configured enterprise ETL/ELT pipeline job definitions.

### `POST /api/v1/data-engineering/etl-jobs`
Create a new pipeline job definition.

### `POST /api/v1/data-engineering/etl-jobs/{id}/run`
Manually trigger execution run for an ETL pipeline job.

### `GET /api/v1/data-engineering/runs/{id}/logs`
Fetch execution logs for a pipeline run.

### `GET /api/v1/data-engineering/datasets`
List all analytics datasets in the catalog.

### `POST /api/v1/data-engineering/datasets`
Register a new analytics dataset.

### `POST /api/v1/data-engineering/datasets/generate-root-files`
Export standard JSON analytics datasets to root `datasets/` directory.

### `GET /api/v1/data-engineering/metadata`
Search metadata catalog and business dictionary.

### `GET /api/v1/data-engineering/feature-groups`
List registered Feature Groups in the Feature Store.

### `POST /api/v1/data-engineering/feature-groups`
Register a new Feature Group.

### `POST /api/v1/data-engineering/features`
Register an individual feature into a Feature Group.

### `GET /api/v1/data-engineering/data-quality`
List data quality profiling inspection reports.

### `POST /api/v1/data-engineering/data-quality/validate`
Run data quality validation rules against a target table or dataset.

### `GET /api/v1/data-engineering/lineage`
Fetch pipeline and dataset lineage DAG graph.

### `GET /api/v1/data-engineering/datalake/objects`
List objects in Data Lake zones (`RAW`, `PROCESSED`, `CURATED`, `ARCHIVE`).

### `GET /api/v1/data-engineering/master-data/records`
List Master Data Management (MDM) golden record entities.

### `GET /api/v1/data-engineering/monitoring/summary`
Fetch Data Engineering platform system status, metrics, and data freshness audit.

