from django.db import models
from django.utils import timezone
from accounts.models import Organization
from screening.models import Screening

class MessageLog(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        SENT = "SENT", "Sent"
        DELIVERED = "DELIVERED", "Delivered"
        READ = "READ", "Read"
        FAILED = "FAILED", "Failed"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="messages")
    to_phone_e164 = models.CharField(max_length=20, db_index=True)
    channel = models.CharField(max_length=16, default="whatsapp")
    template_code = models.CharField(max_length=64, blank=True)   # e.g., RED_EDU_V1 / RED_ASSIST_V1
    language = models.CharField(max_length=16, default="en")      # 'en' | 'hi' | 'local' (or ISO)
    payload = models.JSONField(default=dict, blank=True)          # body/button params, links, etc.
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    provider_msg_id = models.CharField(max_length=128, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=64, blank=True)
    error_title = models.CharField(max_length=255, blank=True)

    # linkage to operational event
    #related_screening = models.ForeignKey(Screening, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    related_screening = models.ForeignKey("screening.Screening", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    related_supply = models.ForeignKey("program.MonthlySupply", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")  # NEW
    
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["scheduled_at", "status"]),
        ]

    def __str__(self):
        return f"{self.to_phone_e164} {self.template_code} {self.status}"
