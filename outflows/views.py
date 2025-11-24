from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Outflow
from accounts.models import Usuario
from .forms import OutflowForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

class OutflowCreateView(LoginRequiredMixin, CreateView):
    model = Outflow
    form_class = OutflowForm
    template_name = 'outflow_create.html'
    success_url = reverse_lazy('spare_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passa o usuário logado para o formulário
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # Define o usuário logado
        return super().form_valid(form)


class OutflowHistoryView(LoginRequiredMixin, ListView):
    model = Outflow
    template_name = 'outflow_history.html'
    context_object_name = 'outflows'
    paginate_by = 10  # Paginação para 10 itens por página

    def get_queryset(self):
        # Recupera o usuário logado
        usuario = get_object_or_404(Usuario, user=self.request.user)
        
        # Filtra todos os Outflows cujo usuário pertence ao mesmo setor
        return Outflow.objects.filter(
            user__usuario__setor=usuario.setor
        ).order_by('-criado_em')
