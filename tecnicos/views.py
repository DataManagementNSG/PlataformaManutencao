from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from .models import Tecnicos
from .forms import TecnicosForm
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Usuario
from django.shortcuts import get_object_or_404, render
from preventiva.models import Preventiva
from django.utils import timezone
from solicitacao.models import Solicitacao

class TecnicosListView(LoginRequiredMixin, ListView):
    model = Tecnicos
    template_name = 'tecnicos_list.html'
    context_object_name = 'tecnicos'

    def get_queryset(self):
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        setor = usuario.setor
        return Tecnicos.objects.filter(setor=setor)

class TecnicosCreateView(LoginRequiredMixin, CreateView):
    model = Tecnicos
    template_name = 'tecnicos_form.html'
    form_class = TecnicosForm  # Utilize o formulário correto
    success_url = reverse_lazy('tecnicos_list')

    def form_valid(self, form):
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        form.instance.setor = usuario.setor
        return super().form_valid(form)

class TecnicosUpdateView(LoginRequiredMixin, UpdateView):
    model = Tecnicos
    template_name = 'tecnicos_form.html'
    form_class = TecnicosForm
    success_url = reverse_lazy('tecnicos_list')

class TecnicosDeleteView(LoginRequiredMixin, DeleteView):
    model = Tecnicos
    template_name = 'tecnicos_confirm_delete.html'
    success_url = reverse_lazy('tecnicos_list')

class TecnicosDetailView(LoginRequiredMixin, DetailView):
    model = Tecnicos
    template_name = 'tecnicos_detail.html'
    context_object_name = 'tecnico'

class TecnicosPreventivaDetailView(LoginRequiredMixin, DetailView):
    model = Tecnicos
    template_name = 'tecnicos_detail_preventiva.html'
    context_object_name = 'tecnico'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tecnico = self.get_object()
        
        # Filtrar todas as preventivas relacionadas ao técnico
        preventivas = Preventiva.objects.filter(
            responsavel=tecnico,
        )
        
        # Contar preventivas abertas (independentemente de estarem atrasadas ou não)
        preventivas_abertas = preventivas.filter(
            status_preventiva=True  # Apenas as preventivas com status aberto
        ).count()
        
        # Contar preventivas fechadas
        preventivas_fechadas = preventivas.filter(
            status_preventiva=False  # Apenas as preventivas com status fechado
        ).count()
        
        # Contar preventivas em atraso
        today = timezone.now().date()  # Obtém a data atual
        preventivas_em_atraso = preventivas.filter(
            status_preventiva=True,  # Apenas as preventivas com status aberto
            data_base_fim__lt=today  # Data de fim menor que a data atual (atrasadas)
        ).count()
        
        context['preventivas_abertas'] = preventivas_abertas
        context['preventivas_fechadas'] = preventivas_fechadas
        context['preventivas_em_atraso'] = preventivas_em_atraso
        context['preventivas'] = preventivas
        context['today'] = today  # Adiciona a data atual ao contexto
        
        return context

# Detalhe de preventiva
def atividade_detail(request, pk):
    preventiva = get_object_or_404(Preventiva, pk=pk)
    return render(request, 'atividade_detail.html', {'object': preventiva})

def solicitacoes_por_tecnico(request, responsavel_id):
    responsavel = get_object_or_404(Tecnicos, id=responsavel_id)
    
    solicitacoes = Solicitacao.objects.filter(
        equipamento__responsavel_mecanico=responsavel
    ) | Solicitacao.objects.filter(
        equipamento__responsavel_eletronico=responsavel
    )
    
    solicitacoes_abertas = solicitacoes.filter(data_fechamento__isnull=True)
    solicitacoes_fechadas = solicitacoes.filter(data_fechamento__isnull=False)
    solicitacoes_atrasadas = solicitacoes_abertas.filter(data_criacao__lt=timezone.now() - timezone.timedelta(days=7))

    contexto = {
        'responsavel': responsavel,
        'solicitacoes': solicitacoes,
        'count_abertas': solicitacoes_abertas.count(),
        'count_fechadas': solicitacoes_fechadas.count(),
        'count_atrasadas': solicitacoes_atrasadas.count(),
    }

    return render(request, 'solicitacoes_por_tecnico.html', contexto)

