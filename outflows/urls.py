from django.urls import path
from . import views


urlpatterns = [
    path('outflows/create/', views.OutflowCreateView.as_view(), name='outflow_create'),
]