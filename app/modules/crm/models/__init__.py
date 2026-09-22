"""CRM Domain ORM Models."""

from app.modules.crm.models.activity import Activity, Note, Task
from app.modules.crm.models.contact import Contact
from app.modules.crm.models.customer import Customer
from app.modules.crm.models.deal import Deal, DealStageHistory
from app.modules.crm.models.lead import Lead
from app.modules.crm.models.pipeline import Pipeline, PipelineStage
from app.modules.crm.models.quotation import Quotation, QuotationItem
from app.modules.crm.models.sales_order import SalesOrder, SalesOrderItem

__all__ = [
    "Lead",
    "Customer",
    "Contact",
    "Pipeline",
    "PipelineStage",
    "Deal",
    "DealStageHistory",
    "Quotation",
    "QuotationItem",
    "SalesOrder",
    "SalesOrderItem",
    "Activity",
    "Note",
    "Task",
]
