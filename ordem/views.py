from django.shortcuts import render, redirect
from .models import Ordem, MaterialOrdem
from .forms import OrdemModelForm, MaterialOrdemModelForm
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.db.models import Sum, F
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from .models import Status, Prioridade
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from accounts.models import Usuario


class OrdemListView(LoginRequiredMixin, ListView):
    model = Ordem
    template_name = 'ordem.html'
    context_object_name = 'ordens'

    def get_queryset(self):
        # Obtém o setor do usuário logado
        user = self.request.user
        try:
            usuario = Usuario.objects.get(user=user)
            setor = usuario.setor
        except Usuario.DoesNotExist:
            setor = None  # Ou algum valor padrão caso o usuário não tenha setor

        # Filtra ordens com base no setor do usuário logado
        ordens = super().get_queryset().filter(equipamento__setor=setor).order_by('-criado_em')

        # Filtros de busca
        search_titulo = self.request.GET.get('titulo')
        search_status = self.request.GET.get('status')
        search_prioridade = self.request.GET.get('prioridade')

        if search_titulo:
            ordens = ordens.filter(titulo__icontains=search_titulo)
        if search_status:
            ordens = ordens.filter(status__nome=search_status)
        if search_prioridade:
            ordens = ordens.filter(prioridade__nome=search_prioridade)

        return ordens

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        context['prioridades'] = Prioridade.objects.all()
        
        ordens = context['ordens']
        for ordem in ordens:
            custo_total = ordem.materiais.aggregate(
                total=Sum(F('quantidade_utilizada') * F('material__valor_unitario'))
            )['total']
            ordem.custo_total = custo_total or 0

        return context
    
def event_list(request):
    events = Ordem.objects.all().values('id', 'titulo', 'data')  # Ajuste conforme seus campos
    events_list = [
        {
            'id': event['id'],
            'title': event['titulo'],
            'start': event['data'].isoformat(),  # Formato ISO para o FullCalendar
        }
        for event in events
    ]
    return JsonResponse(events_list, safe=False)

class NovaOrdemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ordem
    form_class = OrdemModelForm
    template_name = 'nova_ordem.html'
    success_url = reverse_lazy('ordem_list')
    success_message = "Ordem criada com sucesso."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class OrdemDetailView(LoginRequiredMixin, DetailView):
    model = Ordem
    template_name = 'ordem_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordem = self.get_object()
        context['ordem'] = ordem
        return context


class OrdemUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Ordem
    form_class = OrdemModelForm
    template_name = 'ordem_update.html'
    success_message = "Ordem atualizada com sucesso."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('ordem_detail', kwargs={'pk': self.object.pk})


class OrdemDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Ordem
    template_name = 'ordem_delete.html'
    success_url = reverse_lazy('ordem_list')
    success_message = "Ordem deletada com sucesso."


class OrdemMaterialCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MaterialOrdem
    form_class = MaterialOrdemModelForm
    template_name = 'ordem_material.html'
    success_url = reverse_lazy('ordem_list')
    success_message = "Material adicionado à ordem com sucesso."

    def form_valid(self, form):
        ordem_pk = self.kwargs['ordem_pk']
        form.instance.ordem_id = ordem_pk
        material_ordem = form.instance
        material = material_ordem.material
        quantidade_utilizada = material_ordem.quantidade_utilizada

        if quantidade_utilizada <= 0:
            messages.error(self.request, "A quantidade utilizada deve ser maior que 0.")
            return self.form_invalid(form)

        if quantidade_utilizada > material.quantidade:
            messages.error(self.request, "A quantidade utilizada é maior que a quantidade em estoque.")
            return self.form_invalid(form)

        response = super().form_valid(form)
        nova_quantidade = max(material.quantidade - quantidade_utilizada, 0)
        material.quantidade = nova_quantidade
        material.save()

        if material.quantidade <= material.quantidade_minima:
            responsavel_email = material.responsavel.email
            enviar_email_quantidade_minima_atingida(material, responsavel_email)

        return response

def enviar_email_quantidade_minima_atingida(material, responsavel_email):
    subject = 'Alerta de quantidade mínima atingida para: {}'.format(material.nome)
    message = render_to_string('email_ordem.html', {'material': material, 'codigo_sap': material.codigo_sap})
    plain_message = strip_tags(message)
    send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [responsavel_email], html_message=message)


class OrdemMaterialListView(LoginRequiredMixin, ListView):
    model = MaterialOrdem
    template_name = 'ordem_material_list.html'
    context_object_name = 'materiais'

    def get_queryset(self):
        ordem_pk = self.kwargs.get('pk')
        return MaterialOrdem.objects.filter(ordem_id=ordem_pk)

def fechar_ordem(request, pk):
    ordem = get_object_or_404(Ordem, pk=pk)
    status_concluido = get_object_or_404(Status, nome='Concluído')
    ordem.status = status_concluido
    ordem.save()
    messages.success(request, 'A ordem foi fechada com sucesso.')
    return redirect('ordem_list')
