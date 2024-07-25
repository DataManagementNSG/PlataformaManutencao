from django.urls import path
from . import views


urlpatterns = [
    path('equipamento/list/', views.EquipamentoListView.as_view(), name='equipamento_list'),
    path('equipamento/create/', views.EquipamentoCreateView.as_view(), name='equipamento_create'),
    path('equipamento/<int:pk>/detail/', views.EquipamentoDetailView.as_view(), name='equipamento_detail'),
    path('equipamento/<int:pk>/update/', views.EquipamentoUpdateView.as_view(), name='equipamento_update'),
    path('equipamento/<int:pk>/delete/', views.EquipamentoDeleteView.as_view(), name='equipamento_delete'),
    
    path('equipamento/<int:pk>/subcomponente/create/', views.SubcomponenteCreateView.as_view(), name='subcomponente_create'),
    path('subcomponente/<int:pk>/detail/', views.SubcomponenteDetailView.as_view(), name='subcomponente_detail'),
    path('subcomponente/<int:pk>/update/', views.SubcomponenteUpdateView.as_view(), name='subcomponente_update'),
    path('subcomponente/<int:pk>/delete/', views.SubcomponenteDeleteView.as_view(), name='subcomponente_delete'),
    path('subcomponente/<int:pk>/historico/create/', views.HistoricoSubcomponenteCreateView.as_view(), name='historico_create'),
    path('subcomponente/<int:pk>/historico/detail/', views.HistoricoSubcomponenteDetailView.as_view(), name='historico_subcomponente_detail'),
    path('subcomponente/<int:pk>/historico/list/', views.HistoricoSubcomponenteListView.as_view(), name='historico_subcomponente_list'),
]
