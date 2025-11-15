from django.db import models
from django.utils import timezone
from accounts.models import Organization, User
from roster.models import Student
from assist.models import Application
from datetime import timedelta

class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        STOPPED = "STOPPED", "Stopped"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="enrollments")
    application = models.OneToOneField(Application, on_delete=models.PROTECT, related_name="enrollment")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="enrollments")

    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    meta = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.student.full_name} ({self.status})"

    @staticmethod
    def create_for_approved(app: Application, approved_by: User | None):
        start = timezone.now().date()
        end = start + timedelta(days=180)   # 6-month window (approx)
        return Enrollment.objects.create(
            organization=app.organization,
            application=app,
            student=app.student,
            start_date=start,
            end_date=end,
            status=Enrollment.Status.ACTIVE,
            approved_by=approved_by,
        )
