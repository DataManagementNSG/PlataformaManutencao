from django.urls import path
from .views import SolicitacaoListView, SolicitacaoCreateView, SolicitacaoDetailView, SolicitacaoUpdateView, SolicitacaoDeleteView, FecharCartaoSolicitacaoView
from .autocomplete import EquipamentoAutocomplete

urlpatterns = [
    path('solicitacao', SolicitacaoListView.as_view(), name='solicitacao_list'),
    path('criar/', SolicitacaoCreateView.as_view(), name='criar_solicitacao'),
    path('detalhes/<int:pk>/', SolicitacaoDetailView.as_view(), name='detalhes_solicitacao'),
    path('editar/<int:pk>/', SolicitacaoUpdateView.as_view(), name='editar_solicitacao'),
    path('excluir/<int:pk>/', SolicitacaoDeleteView.as_view(), name='excluir_solicitacao'),
    path('fechar/<int:solicitacao_id>/', FecharCartaoSolicitacaoView.as_view(), name='fechar_solicitacao'),
    path('equipamento-autocomplete/', EquipamentoAutocomplete.as_view(), name='equipamento-autocomplete'),
]
