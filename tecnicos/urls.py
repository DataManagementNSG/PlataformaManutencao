# urls.py
from django.urls import path
from .views import atividade_detail
from . import views
from .views import TecnicosListView, TecnicosCreateView, TecnicosUpdateView, TecnicosDeleteView, TecnicosDetailView, TecnicosPreventivaDetailView, TecnicoSolicitacaoDetailView

urlpatterns = [
    path('tecnicos/', TecnicosListView.as_view(), name='tecnicos_list'),
    path('tecnicos/create/', TecnicosCreateView.as_view(), name='tecnicos_create'),
    path('tecnicos/<int:pk>/update/', TecnicosUpdateView.as_view(), name='tecnicos_update'),
    path('tecnicos/<int:pk>/delete/', TecnicosDeleteView.as_view(), name='tecnicos_delete'),
    path('tecnicos/<int:pk>/', TecnicosDetailView.as_view(), name='tecnicos_detail'),
    path('preventivas/<int:pk>/', TecnicosPreventivaDetailView.as_view(), name='preventiva_detail'),
    path('tecnico/<int:pk>/', TecnicoSolicitacaoDetailView.as_view(), name='tecnico_detail'),
    path('atividade/<int:pk>/', atividade_detail, name='atividade_detail'),
]
