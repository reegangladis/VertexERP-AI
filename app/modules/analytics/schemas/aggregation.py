"""Pydantic schemas for multi-dimensional aggregations, date filtering, and charting."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field


class AnalyticsFilterParams(BaseModel):
    """Universal Analytics Query & Filtering Contract."""

    period: Literal[
        "TODAY",
        "THIS_WEEK",
        "THIS_MONTH",
        "THIS_QUARTER",
        "THIS_YEAR",
        "LAST_30_DAYS",
        "LAST_90_DAYS",
        "LAST_12_MONTHS",
        "CUSTOM",
    ] = "THIS_MONTH"
    start_date: datetime | date | None = None
    end_date: datetime | date | None = None
    interval: Literal["day", "week", "month", "quarter", "year"] = "month"
    organization_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    cost_center_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None


class TimeSeriesPoint(BaseModel):
    """Single point in a time-series aggregation bucket."""

    timestamp: str  # ISO date string e.g. "2026-09-01"
    label: str  # Formatted human label e.g. "Sep 2026"
    primary_value: Decimal
    secondary_value: Decimal | None = None
    breakdown: dict[str, Decimal] = Field(default_factory=dict)

    @computed_field
    @property
    def value(self) -> Decimal:
        """Compatibility field for frontend consumers expecting .value."""
        return self.primary_value


class DimensionalBucket(BaseModel):
    """Aggregated metrics grouped by dimension (e.g. Category, Region, Status)."""

    dimension_key: str
    dimension_label: str
    count: int
    total_amount: Decimal
    percentage_share: Decimal = Decimal("0.00")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def percentage(self) -> Decimal:
        """Compatibility field for frontend consumers expecting .percentage."""
        return self.percentage_share


class ChartDatasetResponse(BaseModel):
    """Complete structured dataset for frontend chart rendering."""

    title: str
    chart_type: Literal["LINE", "BAR", "DONUT", "AREA", "FUNNEL", "GAUGE", "TABLE"]
    series: list[TimeSeriesPoint] = Field(default_factory=list)
    breakdowns: list[DimensionalBucket] = Field(default_factory=list)
    summary_metrics: dict[str, Any] = Field(default_factory=dict)
