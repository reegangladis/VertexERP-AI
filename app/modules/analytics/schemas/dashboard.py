"""Pydantic schemas for Dashboards and Dashboard Widgets."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DashboardWidgetBase(BaseModel):
    title: str = Field(..., max_length=128)
    widget_type: Literal[
        "METRIC_CARD",
        "LINE_CHART",
        "BAR_CHART",
        "DONUT_CHART",
        "AREA_CHART",
        "DATA_TABLE",
        "GAUGE",
    ] = "METRIC_CARD"
    kpi_code: str | None = None
    data_source: str = Field(..., max_length=64)
    query_config: dict[str, Any] = Field(default_factory=dict)
    grid_x: int = 0
    grid_y: int = 0
    grid_w: int = 6
    grid_h: int = 4
    sort_order: int = 0


class DashboardWidgetCreate(DashboardWidgetBase):
    pass


class DashboardWidgetResponse(DashboardWidgetBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    dashboard_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardBase(BaseModel):
    code: str = Field(..., max_length=64)
    name: str = Field(..., max_length=128)
    category: Literal[
        "EXECUTIVE", "FINANCE", "SALES", "INVENTORY", "MANUFACTURING", "HR", "CUSTOM"
    ] = "EXECUTIVE"
    description: str | None = None
    layout_config: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    is_system: bool = False
    required_permission: str | None = None


class DashboardCreate(DashboardBase):
    organization_id: uuid.UUID | None = None
    widgets: list[DashboardWidgetCreate] = Field(default_factory=list)


class DashboardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    layout_config: dict[str, Any] | None = None
    is_default: bool | None = None
    required_permission: str | None = None


class DashboardResponse(DashboardBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    widgets: list[DashboardWidgetResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
