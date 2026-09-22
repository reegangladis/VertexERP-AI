"""Pydantic schemas for Analytical Reports and Executions."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AnalyticsReportBase(BaseModel):
    code: str = Field(..., max_length=64)
    title: str = Field(..., max_length=128)
    report_type: Literal[
        "EXECUTIVE_SUMMARY",
        "FINANCIAL_PERFORMANCE",
        "SALES_COHORT",
        "INVENTORY_AGING",
        "MANUFACTURING_EFFICIENCY",
        "HR_PAYROLL_METRICS",
    ] = "EXECUTIVE_SUMMARY"
    description: str | None = None
    parameters_schema: dict[str, Any] = Field(default_factory=dict)
    required_permission: str | None = None
    is_system: bool = True


class AnalyticsReportCreate(AnalyticsReportBase):
    organization_id: uuid.UUID | None = None


class AnalyticsReportResponse(AnalyticsReportBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportExecutionRequest(BaseModel):
    parameters: dict[str, Any] = Field(default_factory=dict)
    format: Literal["JSON", "CSV"] = "JSON"


class ReportExecutionResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    report_code: str
    report_title: str
    executed_by_id: uuid.UUID | None = None
    execution_time_ms: int
    parameters: dict[str, Any]
    result_summary: dict[str, Any]
    headers: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    csv_content: str | None = None
    status: Literal["COMPLETED", "FAILED"] = "COMPLETED"
    created_at: datetime
