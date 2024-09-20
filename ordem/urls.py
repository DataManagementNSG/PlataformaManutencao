from django.urls import path
from .views import OrdemListView, NovaOrdemCreateView, OrdemDetailView, OrdemUpdateView, OrdemDeleteView, OrdemMaterialCreateView, fechar_ordem
from .views import event_list

urlpatterns = [
    path('ordem/list/', OrdemListView.as_view(), name='ordem_list'),
    path('ordens/nova/', NovaOrdemCreateView.as_view(), name='nova_ordem'),
    path('ordens/<int:pk>/', OrdemDetailView.as_view(), name='ordem_detail'),
    path('ordens/<int:pk>/editar/', OrdemUpdateView.as_view(), name='ordem_update'),
    path('ordens/<int:pk>/excluir/', OrdemDeleteView.as_view(), name='ordem_delete'),
    path('ordens/<int:ordem_pk>/material/novo/', OrdemMaterialCreateView.as_view(), name='nova_material_ordem'),
    path('ordem/<int:pk>/fechar/', fechar_ordem, name='fechar_ordem'),
    path('events/', event_list, name='event_list'),
]
