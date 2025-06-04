from django.urls import path
from . import views
from .views import import_items_from_excel, get_item_by_codigo_sap

urlpatterns = [
    path('import-items/', import_items_from_excel, name='import_items'),
    path('spare/list/', views.MaterialListView.as_view(), name='spare_list'),  # Lista de materiais
    path('spare/create/', views.NewMaterialCreateView.as_view(), name='new_spare'),  # Criação de novo material
    path('spare/<int:pk>/detail/', views.MaterialDetailView.as_view(), name='spare_detail'),  # Detalhes do material
    path('spare/<int:pk>/update/', views.MaterialUpdateView.as_view(), name='spare_update'),  # Atualização do material
    path('spare/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='spare_delete'),  # Deleção do material
    path('spare/esgotado/', views.MaterialEsgotadoView.as_view(), name='spare_esgotado'),  # Visualizar materiais esgotados
    path('get-item/', views.get_item_by_codigo_sap, name='get_item_by_codigo_sap'),
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categorias/criar/', views.CategoryCreateView.as_view(), name='category_create'),
    path('download-etiqueta/<int:pk>/', views.get_barcode, name='download_etiqueta'),
]
