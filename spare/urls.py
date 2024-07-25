from django.urls import path
from . import views

urlpatterns = [
    path('spare/list/', views.MaterialListView.as_view(), name='spare_list'),  # Lista de materiais
    path('spare/create/', views.NewMaterialCreateView.as_view(), name='new_spare'),  # Criação de novo material
    path('spare/<int:pk>/detail/', views.MaterialDetailView.as_view(), name='spare_detail'),  # Detalhes do material
    path('spare/<int:pk>/update/', views.MaterialUpdateView.as_view(), name='spare_update'),  # Atualização do material
    path('spare/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='spare_delete'),  # Deleção do material
    path('spare/esgotado/', views.MaterialEsgotadoView.as_view(), name='spare_esgotado'),  # Visualizar materiais esgotados
]
