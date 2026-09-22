"""Finance Domain Central API Router."""

from fastapi import APIRouter

from app.modules.finance.api.v1.account_endpoints import router as account_router
from app.modules.finance.api.v1.bank_endpoints import router as bank_router
from app.modules.finance.api.v1.bill_endpoints import router as bill_router
from app.modules.finance.api.v1.fiscal_endpoints import router as fiscal_router
from app.modules.finance.api.v1.invoice_endpoints import router as invoice_router
from app.modules.finance.api.v1.journal_endpoints import router as journal_router
from app.modules.finance.api.v1.party_endpoints import router as party_router
from app.modules.finance.api.v1.payment_endpoints import router as payment_router
from app.modules.finance.api.v1.report_endpoints import router as report_router

router = APIRouter(prefix="/finance", tags=["Finance & Accounting Domain"])

router.include_router(account_router)
router.include_router(fiscal_router)
router.include_router(party_router)
router.include_router(journal_router)
router.include_router(invoice_router)
router.include_router(bill_router)
router.include_router(payment_router)
router.include_router(bank_router)
router.include_router(report_router)
