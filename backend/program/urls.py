from django.urls import path
from .views import qr_landing, compliance_start, mark_delivered_view
from .views import compliance_form, compliance_success
app_name = "program"

urlpatterns = [
    path("qr/<str:token>/", qr_landing, name="qr_landing"),
    path("program/compliance/start", compliance_start, name="compliance_start"),
    path("program/fulfillment/mark-delivered/<int:supply_id>/", mark_delivered_view, name="mark_delivered"),
    path("program/compliance/<str:token>", compliance_form, name="compliance_form"),
    path("program/compliance/<str:token>/thanks", compliance_success, name="compliance_success"),
    path("program/fulfillment/mark-delivered/<int:supply_id>/", mark_delivered_view, name="mark_delivered"),
]
