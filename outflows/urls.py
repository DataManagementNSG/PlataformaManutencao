from django.urls import path
from . import views


urlpatterns = [
    path('outflows/create/', views.OutflowCreateView.as_view(), name='outflow_create'),
    path('historico/outflow/', views.OutflowHistoryView.as_view(), name='outflow_history'),
]