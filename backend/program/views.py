from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone

from audit.utils import audit_log
from .models import MonthlySupply
from .models import MonthlySupply, ComplianceSubmission
from .forms import ComplianceForm
from .services import mark_supply_delivered,apply_gating_after_submission
from accounts.decorators import require_roles
from accounts.models import Role

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


# def compliance_start(request):
#     """
#     Placeholder page that will link into Sprint 6 compliance form.
#     Accepts ?token=<qr_token>
#     """
#     token = request.GET.get("token") or ""
#     if not token:
#         return HttpResponseBadRequest("Missing token")
#     supply = get_object_or_404(MonthlySupply, qr_token=token)
#     return render(request, "program/compliance_start.html", {
#         "supply": supply,
#         "due": supply.compliance_due_at,
#         "delivered_on": supply.delivered_on,
#     })


# Optional helper for lightweight fulfillment outside admin (RBAC kept simple here).
from accounts.decorators import require_roles
from accounts.models import Role

# @require_roles(Role.ORG_ADMIN, Role.SAPA_ADMIN, Role.INDITECH, allow_superuser=True)
# def mark_delivered_view(request, supply_id: int):
#     from .services import mark_supply_delivered
#     if request.method != "POST":
#         return HttpResponseBadRequest("POST required")
#     supply = get_object_or_404(MonthlySupply, pk=supply_id)
#     mark_supply_delivered(supply, delivered_on=None, actor=request.user)
#     # redirect to admin change page or a list you already have
#     return redirect(f"/admin/program/monthlysupply/{supply.id}/change/")

def compliance_form(request, token: str):
    ms = get_object_or_404(MonthlySupply, qr_token=token)
    comp, _ = ComplianceSubmission.objects.get_or_create(monthly_supply=ms)

    if request.method == "POST":
        form = ComplianceForm(request.POST)
        if form.is_valid():
            comp.status = form.cleaned_data["status"]
            comp.submitted_at = timezone.now()
            comp.responses = {"notes": form.cleaned_data.get("notes","")}
            comp.save(update_fields=["status","submitted_at","responses","updated_at"])

            apply_gating_after_submission(ms)
            audit_log(user=None, org=ms.enrollment.organization, action="COMPLIANCE_SUBMITTED",
                      target=comp, payload={"status": comp.status, "supply_id": ms.id})

            return redirect(reverse("program:compliance_success", args=[ms.qr_token]))
    else:
        form = ComplianceForm(initial={"status": "COMPLIANT"})

    return render(request, "program/compliance_form.html", {
        "supply": ms, "form": form,
        "due": ms.compliance_due_at, "delivered_on": ms.delivered_on
    })

def compliance_success(request, token: str):
    ms = get_object_or_404(MonthlySupply, qr_token=token)
    comp = getattr(ms, "compliance", None)
    return render(request, "program/compliance_success.html", {"supply": ms, "comp": comp})

def compliance_start(request):
    """
    Backward-compatibility for Sprint 5 URL:
    /program/compliance/start?token=<qr_token>
    """
    token = request.GET.get("token")
    if not token:
        return HttpResponseBadRequest("Missing token")
    return redirect(reverse("program:compliance_form", args=[token]))

@require_roles(Role.ORG_ADMIN, Role.SAPA_ADMIN, Role.INDITECH, allow_superuser=True)
def mark_delivered_view(request, supply_id: int):
    """
    Legacy-compatible wrapper so older URLs that point to 'mark_delivered_view'
    continue to work. Internally we call the new helper mark_supply_delivered().
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    ms = get_object_or_404(MonthlySupply, pk=supply_id)
    mark_supply_delivered(ms, delivered_on=None, actor=request.user)
    return redirect(f"/admin/program/monthlysupply/{ms.id}/change/")
