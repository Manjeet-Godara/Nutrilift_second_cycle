from datetime import date
from django.db import transaction
from django.utils import timezone
from audit.utils import audit_log
from .models import MonthlySupply

@transaction.atomic
def mark_supply_delivered(supply: MonthlySupply, delivered_on: date | None, actor=None):
    supply.set_delivered(delivered_on or timezone.now().date(), save=True)
    if actor:
        audit_log(actor, supply.enrollment.organization, "SUPPLY_DELIVERED",
                  target=supply, payload={"month_index": supply.month_index,
                                          "compliance_due_at": supply.compliance_due_at.isoformat()})
    return supply
