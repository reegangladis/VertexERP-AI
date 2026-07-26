import uuid
import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.schemas.finance import (
    JournalEntryCreate,
    JournalEntryLineCreate,
    CustomerInvoiceCreate,
    InvoiceItemCreate,
)
from app.services.finance_service import FinanceService
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_double_entry_balance_validation():
    db_mock = AsyncMock()
    service = FinanceService(db_mock)
    org_id = uuid.uuid4()

    # Unbalanced entry (Debit 100 != Credit 50)
    unbalanced_data = JournalEntryCreate(
        entry_date=date.today(),
        narration="Unbalanced Test",
        lines=[
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=100.0, credit=0.0),
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=0.0, credit=50.0),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_journal_entry(org_id, unbalanced_data)
    
    assert exc_info.value.status_code == 400
    assert "Double-entry accounting error" in exc_info.value.detail

@pytest.mark.asyncio
async def test_balanced_journal_entry():
    db_mock = AsyncMock()
    service = FinanceService(db_mock)
    org_id = uuid.uuid4()

    balanced_data = JournalEntryCreate(
        entry_number="JE-TEST-001",
        entry_date=date.today(),
        narration="Balanced Test",
        lines=[
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=500.0, credit=0.0),
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=0.0, credit=500.0),
        ]
    )

    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()

    service.journal_repo.create = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), entry_number="JE-TEST-001"))
    service.journal_repo.get_with_lines = AsyncMock(return_value=MagicMock(
        id=uuid.uuid4(),
        entry_number="JE-TEST-001",
        lines=[]
    ))

    result = await service.create_journal_entry(org_id, balanced_data)
    assert result.entry_number == "JE-TEST-001"
