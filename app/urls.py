from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts.views import registro_view, login_view, logout_view
from tecnicos.views import TecnicosListView, TecnicosCreateView, TecnicosUpdateView, TecnicosDeleteView, TecnicosDetailView, TecnicosPreventivaDetailView
from spare.views import ListView, CreateView, DetailView, UpdateView, DeleteView
from inflows.views import InflowCreateView
from outflows.views import OutflowCreateView
from solicitacao.views import SolicitacaoListView, SolicitacaoCreateView, SolicitacaoDetailView, SolicitacaoUpdateView, SolicitacaoDeleteView, FecharCartaoSolicitacaoView
from equipamento.views import ListView as EquipamentoListView, CreateView as EquipamentoCreateView, DetailView as EquipamentoDetailView, UpdateView as EquipamentoUpdateView, DeleteView as EquipamentoDeleteView
from ordem.views import ListView as OrdemListView, CreateView as OrdemCreateView, DetailView as OrdemDetailView, UpdateView as OrdemUpdateView, DeleteView as OrdemDeleteView
from preventiva.views import PreventivaFechadaListView, PreventivaDetailView, PreventivaCreateView, PreventivaUpdateView, PreventivaDeleteView, upload_file, relatorio_excel, atualizar_status_sap, materiais_por_responsavel, solicitacoes_por_tecnico

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registro/', registro_view, name='registro'),
    path('login', login_view, name = 'login'),
    path('', views.home, name = 'home'),
    path('logout/', logout_view, name = 'logout'),
    path('', include('tecnicos.urls')),
    path('', include('spare.urls')),
    path('', include('inflows.urls')),
    path('', include('outflows.urls')),
    path('', include('solicitacao.urls')),
    path('', include('equipamento.urls')),
    path('', include('ordem.urls')),
    path('', include('preventiva.urls')),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)