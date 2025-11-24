from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from . import models, forms
from .models import Inflow
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from accounts.models import Usuario  # Importa o modelo que contém o setor

class InflowCreateView(LoginRequiredMixin, CreateView):
    model = models.Inflow
    template_name = 'inflow_create.html'
    form_class = forms.InflowForm
    success_url = reverse_lazy('spare_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passe o usuário logado para o formulário
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # Define o usuário logado
        return super().form_valid(form)


class InflowHistoryView(LoginRequiredMixin, ListView):
    model = Inflow
    template_name = 'inflow_history.html'
    context_object_name = 'inflows'
    paginate_by = 10  # Adiciona paginação (10 registros por página)

    def get_queryset(self):
        # Recupera o setor do usuário logado
        usuario = get_object_or_404(Usuario, user=self.request.user)
        # Retorna todos os inflows de usuários do mesmo setor
        return Inflow.objects.filter(user__usuario__setor=usuario.setor).order_by('-criado_em')
