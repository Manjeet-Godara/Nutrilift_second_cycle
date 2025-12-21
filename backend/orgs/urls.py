from django.urls import path
from .views import org_start, grantor_home

app_name = "orgs"
urlpatterns = [
    path("orgs/start", org_start, name="org_start"),
    path("orgs/grantor", grantor_home, name="grantor_home"),
]
