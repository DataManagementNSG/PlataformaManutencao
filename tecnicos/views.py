from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from .models import Tecnicos
from .forms import TecnicosForm
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Usuario
from django.shortcuts import get_object_or_404

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
