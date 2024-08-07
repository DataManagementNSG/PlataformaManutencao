from django.views.generic import CreateView
from django.urls import reverse_lazy
from . import models, forms
from django.contrib.auth.mixins import LoginRequiredMixin

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
        form.instance.entrada_por = self.request.user  # Define o usuário logado como o responsável pela entrada
        return super().form_valid(form)
