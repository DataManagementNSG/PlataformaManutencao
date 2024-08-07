from django.urls import path
from . import views


urlpatterns = [
    path('inflow/create/', views.InflowCreateView.as_view(), name='inflow_create'),
]