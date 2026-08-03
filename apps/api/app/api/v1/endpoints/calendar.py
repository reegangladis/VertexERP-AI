import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.calendar import (
    BusinessCalendarRepository,
    HolidayRepository,
    WorkingDayRepository,
)
from app.schemas.calendar import (
    BusinessCalendarCreate,
    BusinessCalendarResponse,
    BusinessCalendarUpdate,
    HolidayCreate,
    HolidayResponse,
    WorkingDayCreate,
    WorkingDayResponse,
)
from app.services.calendar_service import CalendarService

router = APIRouter()


def get_calendar_service(
    db: AsyncSession = Depends(get_db_session),
) -> CalendarService:
    return CalendarService(
        BusinessCalendarRepository(db),
        HolidayRepository(db),
        WorkingDayRepository(db),
    )


@router.post("", response_model=BusinessCalendarResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar(
    data: BusinessCalendarCreate,
    service: CalendarService = Depends(get_calendar_service),
):
    return await service.create(data)


@router.get("", response_model=list[BusinessCalendarResponse])
async def list_calendars(
    organization_id: uuid.UUID | None = None,
    service: CalendarService = Depends(get_calendar_service),
):
    if organization_id:
        return await service.get_by_org(organization_id)
    items, _ = await service.get_multi()
    return items


@router.get("/{id}", response_model=BusinessCalendarResponse)
async def get_calendar(
    id: uuid.UUID,
    service: CalendarService = Depends(get_calendar_service),
):
    return await service.get_calendar_details(id)


@router.put("/{id}", response_model=BusinessCalendarResponse)
async def update_calendar(
    id: uuid.UUID,
    data: BusinessCalendarUpdate,
    service: CalendarService = Depends(get_calendar_service),
):
    item = await service.update(id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found"
        )
    return item


@router.delete("/{id}", response_model=BusinessCalendarResponse)
async def delete_calendar(
    id: uuid.UUID,
    service: CalendarService = Depends(get_calendar_service),
):
    item = await service.delete(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found"
        )
    return item


@router.post("/{id}/holidays", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def add_holiday(
    id: uuid.UUID,
    data: HolidayCreate,
    service: CalendarService = Depends(get_calendar_service),
):
    return await service.add_holiday(id, data)


@router.post("/{id}/working-days", response_model=WorkingDayResponse, status_code=status.HTTP_201_CREATED)
async def add_working_day(
    id: uuid.UUID,
    data: WorkingDayCreate,
    service: CalendarService = Depends(get_calendar_service),
):
    return await service.add_working_day(id, data)
