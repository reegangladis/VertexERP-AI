"""Financial Reports Pydantic Schemas."""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class TrialBalanceLine(BaseModel):
    account_id: uuid.UUID
    account_code: str
    account_name: str
    account_type: str
    debit_total: Decimal
    credit_total: Decimal
    net_debit: Decimal
    net_credit: Decimal


class TrialBalanceResponse(BaseModel):
    as_of_date: date
    lines: list[TrialBalanceLine]
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool


class BalanceSheetLine(BaseModel):
    account_id: uuid.UUID
    account_code: str
    account_name: str
    account_category: str
    balance: Decimal


class BalanceSheetCategorySection(BaseModel):
    category: str
    lines: list[BalanceSheetLine]
    subtotal: Decimal


class BalanceSheetResponse(BaseModel):
    as_of_date: date
    assets: list[BalanceSheetCategorySection]
    liabilities: list[BalanceSheetCategorySection]
    equity: list[BalanceSheetCategorySection]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    total_liabilities_and_equity: Decimal
    is_balanced: bool


class ProfitLossLine(BaseModel):
    account_id: uuid.UUID
    account_code: str
    account_name: str
    account_category: str
    amount: Decimal


class ProfitLossResponse(BaseModel):
    start_date: date
    end_date: date
    revenues: list[ProfitLossLine]
    expenses: list[ProfitLossLine]
    total_revenue: Decimal
    total_expense: Decimal
    net_income: Decimal
