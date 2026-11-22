"""Financial Reporting Service (Trial Balance, Balance Sheet, P&L)."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.finance.models.account import AccountType
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.repositories.journal_repository import GeneralLedgerRepository
from app.modules.finance.schemas.reports import (
    BalanceSheetCategorySection,
    BalanceSheetLine,
    BalanceSheetResponse,
    ProfitLossLine,
    ProfitLossResponse,
    TrialBalanceLine,
    TrialBalanceResponse,
)


class FinancialReportService:
    """Service computing high-integrity financial statements directly from the General Ledger."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.account_repo = AccountRepository(session)
        self.gl_repo = GeneralLedgerRepository(session)

    async def get_trial_balance(
        self,
        as_of_date: date,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> TrialBalanceResponse:
        """Compute Trial Balance summing all debit and credit totals across all accounts."""
        accounts = await self.account_repo.list_by_org(tenant_id, org_id, limit=500)
        lines: list[TrialBalanceLine] = []

        total_debit = Decimal("0.0000")
        total_credit = Decimal("0.0000")

        for acct in accounts:
            debit, credit = await self.gl_repo.get_account_totals(
                acct.id, tenant_id, org_id, as_of_date=as_of_date
            )
            d_dec = Decimal(str(debit))
            c_dec = Decimal(str(credit))

            if d_dec == 0 and c_dec == 0:
                continue

            total_debit += d_dec
            total_credit += c_dec

            net_debit = d_dec - c_dec if d_dec >= c_dec else Decimal("0.0000")
            net_credit = c_dec - d_dec if c_dec > d_dec else Decimal("0.0000")

            lines.append(
                TrialBalanceLine(
                    account_id=acct.id,
                    account_code=acct.code,
                    account_name=acct.name,
                    account_type=acct.account_type,
                    debit_total=d_dec,
                    credit_total=c_dec,
                    net_debit=net_debit,
                    net_credit=net_credit,
                )
            )

        is_balanced = total_debit == total_credit

        return TrialBalanceResponse(
            as_of_date=as_of_date,
            lines=lines,
            total_debit=total_debit,
            total_credit=total_credit,
            is_balanced=is_balanced,
        )

    async def get_profit_and_loss(
        self,
        start_date: date,
        end_date: date,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> ProfitLossResponse:
        """Compute Profit & Loss (Income Statement) for a date range."""
        accounts = await self.account_repo.list_by_org(tenant_id, org_id, limit=500)
        revenues: list[ProfitLossLine] = []
        expenses: list[ProfitLossLine] = []

        total_revenue = Decimal("0.0000")
        total_expense = Decimal("0.0000")

        for acct in accounts:
            if acct.account_type not in [AccountType.REVENUE, AccountType.EXPENSE]:
                continue

            debit, credit = await self.gl_repo.get_account_totals(
                acct.id, tenant_id, org_id, as_of_date=end_date
            )
            d_dec = Decimal(str(debit))
            c_dec = Decimal(str(credit))

            if acct.account_type == AccountType.REVENUE:
                # Revenue net = Credit - Debit
                amount = c_dec - d_dec
                if amount != 0:
                    total_revenue += amount
                    revenues.append(
                        ProfitLossLine(
                            account_id=acct.id,
                            account_code=acct.code,
                            account_name=acct.name,
                            account_category=acct.account_category,
                            amount=amount,
                        )
                    )
            elif acct.account_type == AccountType.EXPENSE:
                # Expense net = Debit - Credit
                amount = d_dec - c_dec
                if amount != 0:
                    total_expense += amount
                    expenses.append(
                        ProfitLossLine(
                            account_id=acct.id,
                            account_code=acct.code,
                            account_name=acct.name,
                            account_category=acct.account_category,
                            amount=amount,
                        )
                    )

        net_income = total_revenue - total_expense

        return ProfitLossResponse(
            start_date=start_date,
            end_date=end_date,
            revenues=revenues,
            expenses=expenses,
            total_revenue=total_revenue,
            total_expense=total_expense,
            net_income=net_income,
        )

    async def get_balance_sheet(
        self,
        as_of_date: date,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> BalanceSheetResponse:
        """Compute Balance Sheet satisfying Assets = Liabilities + Equity."""
        accounts = await self.account_repo.list_by_org(tenant_id, org_id, limit=500)

        assets_by_cat: dict[str, list[BalanceSheetLine]] = {}
        liabilities_by_cat: dict[str, list[BalanceSheetLine]] = {}
        equity_by_cat: dict[str, list[BalanceSheetLine]] = {}

        total_assets = Decimal("0.0000")
        total_liabilities = Decimal("0.0000")
        total_equity = Decimal("0.0000")

        for acct in accounts:
            debit, credit = await self.gl_repo.get_account_totals(
                acct.id, tenant_id, org_id, as_of_date=as_of_date
            )
            d_dec = Decimal(str(debit))
            c_dec = Decimal(str(credit))

            if acct.account_type == AccountType.ASSET:
                balance = d_dec - c_dec
                if balance != 0:
                    total_assets += balance
                    assets_by_cat.setdefault(acct.account_category, []).append(
                        BalanceSheetLine(
                            account_id=acct.id,
                            account_code=acct.code,
                            account_name=acct.name,
                            account_category=acct.account_category,
                            balance=balance,
                        )
                    )

            elif acct.account_type == AccountType.LIABILITY:
                balance = c_dec - d_dec
                if balance != 0:
                    total_liabilities += balance
                    liabilities_by_cat.setdefault(acct.account_category, []).append(
                        BalanceSheetLine(
                            account_id=acct.id,
                            account_code=acct.code,
                            account_name=acct.name,
                            account_category=acct.account_category,
                            balance=balance,
                        )
                    )

            elif acct.account_type == AccountType.EQUITY:
                balance = c_dec - d_dec
                if balance != 0:
                    total_equity += balance
                    equity_by_cat.setdefault(acct.account_category, []).append(
                        BalanceSheetLine(
                            account_id=acct.id,
                            account_code=acct.code,
                            account_name=acct.name,
                            account_category=acct.account_category,
                            balance=balance,
                        )
                    )

        # Include Retained Earnings from Net Income (Revenue - Expenses) into Equity
        pnl = await self.get_profit_and_loss(
            date(as_of_date.year, 1, 1), as_of_date, tenant_id, org_id
        )
        if pnl.net_income != 0:
            total_equity += pnl.net_income
            equity_by_cat.setdefault("RETAINED_EARNINGS", []).append(
                BalanceSheetLine(
                    account_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    account_code="3999",
                    account_name="Current Period Net Earnings",
                    account_category="RETAINED_EARNINGS",
                    balance=pnl.net_income,
                )
            )

        asset_sections = [
            BalanceSheetCategorySection(
                category=cat,
                lines=lines,
                subtotal=sum(l.balance for l in lines),
            )
            for cat, lines in assets_by_cat.items()
        ]

        liability_sections = [
            BalanceSheetCategorySection(
                category=cat,
                lines=lines,
                subtotal=sum(l.balance for l in lines),
            )
            for cat, lines in liabilities_by_cat.items()
        ]

        equity_sections = [
            BalanceSheetCategorySection(
                category=cat,
                lines=lines,
                subtotal=sum(l.balance for l in lines),
            )
            for cat, lines in equity_by_cat.items()
        ]

        total_liabilities_and_equity = total_liabilities + total_equity
        is_balanced = total_assets == total_liabilities_and_equity

        return BalanceSheetResponse(
            as_of_date=as_of_date,
            assets=asset_sections,
            liabilities=liability_sections,
            equity=equity_sections,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            total_equity=total_equity,
            total_liabilities_and_equity=total_liabilities_and_equity,
            is_balanced=is_balanced,
        )
