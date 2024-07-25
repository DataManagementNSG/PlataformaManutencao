# urls.py
from django.urls import path
from .views import TecnicosListView, TecnicosCreateView, TecnicosUpdateView, TecnicosDeleteView, TecnicosDetailView

urlpatterns = [
    path('tecnicos/', TecnicosListView.as_view(), name='tecnicos_list'),
    path('tecnicos/adicionar/', TecnicosCreateView.as_view(), name='tecnicos_create'),
    path('tecnicos/editar/<int:pk>/', TecnicosUpdateView.as_view(), name='tecnicos_update'),
    path('tecnicos/deletar/<int:pk>/', TecnicosDeleteView.as_view(), name='tecnicos_delete'),
    path('tecnicos/<int:pk>/', TecnicosDetailView.as_view(), name='tecnicos_detail'),
]
