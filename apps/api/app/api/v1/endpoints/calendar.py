import uuid
from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.calendar import BusinessCalendar, WorkingDay, Holiday
from app.repositories.org_mgmt import CalendarRepository, WorkingDayRepository, HolidayRepository
from app.services.org_mgmt import BusinessCalendarService
from app.schemas.org_mgmt import (
    BusinessCalendarResponse,
    BusinessCalendarCreate,
    BusinessCalendarUpdate,
    WorkingDayResponse,
    WorkingDayCreate,
    HolidayResponse,
    HolidayCreate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_calendar_service(db: AsyncSession = Depends(get_db_session)):
    return BusinessCalendarService(
        CalendarRepository(db),
        WorkingDayRepository(db),
        HolidayRepository(db)
    )

@router.get("", response_model=APIResponse[List[BusinessCalendarResponse]])
async def list_calendars(
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    calendars = await service.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Calendars retrieved successfully",
        data=[BusinessCalendarResponse.model_validate(c) for c in calendars]
    )

@router.post("", response_model=APIResponse[BusinessCalendarResponse])
async def create_calendar(
    payload: BusinessCalendarCreate,
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id

    # If setting to active, deactivate others
    if payload.is_active:
        existing = await service.get_by_org(current_user.organization_id)
        for old in existing:
            if old.is_active:
                await service.repository.update(old, {"is_active": False})

    calendar = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Calendar created successfully",
        data=BusinessCalendarResponse.model_validate(calendar)
    )

@router.get("/{id}", response_model=APIResponse[BusinessCalendarResponse])
async def get_calendar(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Calendar retrieved",
        data=BusinessCalendarResponse.model_validate(calendar)
    )

@router.put("/{id}", response_model=APIResponse[BusinessCalendarResponse])
async def update_calendar(
    id: uuid.UUID,
    payload: BusinessCalendarUpdate,
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")

    if payload.is_active:
        existing = await service.get_by_org(current_user.organization_id)
        for old in existing:
            if old.id != id and old.is_active:
                await service.repository.update(old, {"is_active": False})

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Calendar updated successfully",
        data=BusinessCalendarResponse.model_validate(updated)
    )

@router.delete("/{id}", response_model=APIResponse[BusinessCalendarResponse])
async def delete_calendar(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Calendar deleted successfully",
        data=BusinessCalendarResponse.model_validate(deleted)
    )

@router.get("/{id}/working-days", response_model=APIResponse[List[WorkingDayResponse]])
async def list_working_days(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")
        
    days = await service.working_day_repo.get_by_calendar(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Working days retrieved",
        data=[WorkingDayResponse.model_validate(d) for d in days]
    )

@router.post("/{id}/working-days", response_model=APIResponse[List[WorkingDayResponse]])
async def configure_working_days(
    id: uuid.UUID,
    payload: List[WorkingDayCreate],
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")

    data = [item.model_dump() for item in payload]
    configured = await service.configure_working_days(current_user.organization_id, id, data)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Working days configured successfully",
        data=[WorkingDayResponse.model_validate(d) for d in configured]
    )

@router.get("/{id}/holidays", response_model=APIResponse[List[HolidayResponse]])
async def list_holidays(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")

    holidays = await service.holiday_repo.get_by_calendar(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Holidays retrieved",
        data=[HolidayResponse.model_validate(h) for h in holidays]
    )

@router.post("/{id}/holidays", response_model=APIResponse[List[HolidayResponse]])
async def configure_holidays(
    id: uuid.UUID,
    payload: List[HolidayCreate],
    current_user: User = Depends(get_current_user),
    service: BusinessCalendarService = Depends(get_calendar_service)
):
    calendar = await service.get(id)
    if not calendar or calendar.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Calendar not found")

    data = [item.model_dump() for item in payload]
    configured = await service.configure_holidays(current_user.organization_id, id, data)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Holidays configured successfully",
        data=[HolidayResponse.model_validate(h) for h in configured]
    )
