from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Outflow
from .forms import OutflowForm
from django.contrib.auth.mixins import LoginRequiredMixin

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
        form.instance.retirado_por = self.request.user  # Define o usuário logado como o responsável pela saída
        return super().form_valid(form)

class OutflowHistoryView(LoginRequiredMixin, ListView):
    model = Outflow
    template_name = 'outflow_history.html'
    context_object_name = 'outflows'
    paginate_by = 10  # Paginação para 10 itens por página

    def get_queryset(self):
        return Outflow.objects.filter(user=self.request.user).order_by('-criado_em')

