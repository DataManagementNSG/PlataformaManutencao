from django.urls import path
from . import views
from .views import (
    PreventivaFechadaListView,
    PreventivaDetailView,
    PreventivaCreateView,
    PreventivaUpdateView,
    PreventivaDeleteView,
    upload_file,
    relatorio_excel,
    atualizar_status_sap,
    materiais_por_responsavel,
    solicitacoes_por_tecnico,
    preventiva_list,
    fechar_preventiva_view,
)

urlpatterns = [
    path('preventivas/fechadas/', PreventivaFechadaListView.as_view(), name='preventiva_fechada_list'),
    path('preventivas/list/', preventiva_list, name='preventiva_list'),
    path('preventiva/<int:pk>/fechar/', fechar_preventiva_view, name='fechar_preventiva'),
    path('preventivas/<int:pk>/', PreventivaDetailView.as_view(), name='preventiva_detail'),
    path('preventivas/criar/', PreventivaCreateView.as_view(), name='preventiva_create'),
    path('preventivas/<int:pk>/editar/', PreventivaUpdateView.as_view(), name='preventiva_update'),
    path('preventivas/<int:pk>/deletar/', PreventivaDeleteView.as_view(), name='preventiva_delete'),
    path('upload/', upload_file, name='upload_file'),
    path('relatorio/excel/', relatorio_excel, name='relatorio_excel'),
    path('atualizar/status_sap/', atualizar_status_sap, name='atualizar_status_sap'),
    path('materiais/responsavel/<int:responsavel_id>/', materiais_por_responsavel, name='materiais_por_responsavel'),
    path('solicitacoes/tecnico/<int:responsavel_id>/', solicitacoes_por_tecnico, name='solicitacoes_por_tecnico'),
]
