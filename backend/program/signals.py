# backend/program/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MonthlySupply, ComplianceSubmission

@receiver(post_save, sender=MonthlySupply)
def ensure_compliance_row(sender, instance: MonthlySupply, created, **kwargs):
    """
    Ensure every MonthlySupply has a ComplianceSubmission row.
    Use get_or_create for idempotency (safe on bulk/backfills).
    """
    if created:
        ComplianceSubmission.objects.get_or_create(monthly_supply=instance)
