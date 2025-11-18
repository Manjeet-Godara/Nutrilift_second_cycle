from django.urls import path
from .views import qr_landing, compliance_start, mark_delivered_view

app_name = "program"

urlpatterns = [
    path("qr/<str:token>/", qr_landing, name="qr_landing"),
    path("program/compliance/start", compliance_start, name="compliance_start"),
    path("program/fulfillment/mark-delivered/<int:supply_id>/", mark_delivered_view, name="mark_delivered"),
]
