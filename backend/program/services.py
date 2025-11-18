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

def apply_gating_after_submission(supply: MonthlySupply):
    """
    If month m is COMPLIANT -> set month (m+1).ok_to_ship_next = True
    Else -> False. Month 6 has no next-supply.
    """
    comp = getattr(supply, "compliance", None)
    if not comp:
        return
    next_ms = MonthlySupply.objects.filter(enrollment=supply.enrollment, month_index=supply.month_index + 1).first()
    if not next_ms:
        return
    next_ms.ok_to_ship_next = (comp.status == comp.Status.COMPLIANT)
    next_ms.save(update_fields=["ok_to_ship_next", "updated_at"])
