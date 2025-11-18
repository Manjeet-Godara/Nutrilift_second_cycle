from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone

from audit.utils import audit_log
from .models import MonthlySupply

def qr_landing(request, token: str):
    """
    Public landing after scanning a pack QR.
    Shows instructions + link to start the compliance form (Sprint 6).
    """
    supply = get_object_or_404(MonthlySupply, qr_token=token)
    org = supply.enrollment.organization
    student = supply.enrollment.student

    audit_log(user=None, org=org, action="QR_OPENED", target=supply, payload={"month": supply.month_index})

    return render(request, "program/qr_landing.html", {
        "supply": supply,
        "student": student,
        "org": org,
        "is_delivered": bool(supply.delivered_on),
    })


def compliance_start(request):
    """
    Placeholder page that will link into Sprint 6 compliance form.
    Accepts ?token=<qr_token>
    """
    token = request.GET.get("token") or ""
    if not token:
        return HttpResponseBadRequest("Missing token")
    supply = get_object_or_404(MonthlySupply, qr_token=token)
    return render(request, "program/compliance_start.html", {
        "supply": supply,
        "due": supply.compliance_due_at,
        "delivered_on": supply.delivered_on,
    })


# Optional helper for lightweight fulfillment outside admin (RBAC kept simple here).
from accounts.decorators import require_roles
from accounts.models import Role

@require_roles(Role.ORG_ADMIN, Role.SAPA_ADMIN, Role.INDITECH, allow_superuser=True)
def mark_delivered_view(request, supply_id: int):
    from .services import mark_supply_delivered
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    supply = get_object_or_404(MonthlySupply, pk=supply_id)
    mark_supply_delivered(supply, delivered_on=None, actor=request.user)
    # redirect to admin change page or a list you already have
    return redirect(f"/admin/program/monthlysupply/{supply.id}/change/")
