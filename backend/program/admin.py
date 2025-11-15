from django.contrib import admin
from .models import Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("organization","student","status","start_date","end_date","approved_by")
    list_filter = ("organization","status")
    search_fields = ("student__first_name","student__last_name")
