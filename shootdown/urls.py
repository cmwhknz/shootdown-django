from django.urls import path

from . import views
from . import api_residual_value

app_name = "shootdown"

urlpatterns = [
    # Main page - residual value 
    path("", views.residual_value, name="residual_value"),

    # API endpoints
    path("api/residual_value/", api_residual_value.get_residual_value, name="api_residual_value"),
]