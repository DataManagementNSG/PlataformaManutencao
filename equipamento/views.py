from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .forms import EquipamentoModelForm, SubcomponenteForm, HistoricoSubcomponenteForm
from spare.models import Criticidade
from .models import Equipamento, Area, Linha, Subcomponente, HistoricoSubcomponente
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Usuario
from tecnicos.models import Tecnicos

class EquipamentoListView(LoginRequiredMixin, ListView):
    model = Equipamento
    template_name = 'equipamento.html'
    context_object_name = 'equipamentos'
    paginate_by = 12  # Defina o número de itens por página

    def get_queryset(self):
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        setor = usuario.setor

        # Recuperar os equipamentos associados ao setor do usuário logado
        equipamentos = Equipamento.objects.filter(setor=setor).order_by('nome')

        # Recuperar parâmetros de busca da requisição GET
        search_nome = self.request.GET.get('nome', '')
        search_descricao = self.request.GET.get('descricao', '')
        search_linha = self.request.GET.get('linha', '')
        search_area = self.request.GET.get('area', '')
        search_criticidade = self.request.GET.get('criticidade', '')

        # Aplicar filtros se os parâmetros de busca estiverem presentes
        if search_nome:
            equipamentos = equipamentos.filter(nome__icontains=search_nome)
        if search_descricao:
            equipamentos = equipamentos.filter(descricao__icontains=search_descricao)
        if search_linha:
            equipamentos = equipamentos.filter(linha__nome=search_linha)
        if search_area:
            equipamentos = equipamentos.filter(area__nome=search_area)
        if search_criticidade:
            equipamentos = equipamentos.filter(criticidade__icontains=search_criticidade)

        # Combinar pesquisa em linha e área
        if search_linha and search_area:
            equipamentos = equipamentos.filter(
                Q(linha__nome=search_linha) & Q(area__nome=search_area)
            )

        return equipamentos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adicionar apenas as linhas associadas ao setor do usuário logado ao contexto
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        setor = usuario.setor
        context['linhas'] = Linha.objects.filter(setor=setor)

        # Adicionar áreas e criticidades ao contexto
        context['areas'] = Area.objects.all()
        context['criticidades'] = Criticidade.objects.all()

        # Adicionar parâmetros de busca ao contexto
        context['search_nome'] = self.request.GET.get('nome', '')
        context['search_descricao'] = self.request.GET.get('descricao', '')
        context['search_linha'] = self.request.GET.get('linha', '')
        context['search_area'] = self.request.GET.get('area', '')
        context['search_criticidade'] = self.request.GET.get('criticidade', '')

        return context

class EquipamentoCreateView(LoginRequiredMixin, CreateView):
    model = Equipamento
    form_class = EquipamentoModelForm
    template_name = 'equipamento_create.html'
    success_url = reverse_lazy('equipamento_list')

    def form_valid(self, form):
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        form.instance.setor = usuario.setor
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        setor = usuario.setor

        # Filtrar opções no formulário com base no setor
        if 'linha' in form.fields:
            form.fields['linha'].queryset = Linha.objects.filter(setor=setor)
        if 'area' in form.fields:
            form.fields['area'].queryset = Area.objects.filter(setor=setor)
        if 'responsavel_mecanico' in form.fields:
            form.fields['responsavel_mecanico'].queryset = Tecnicos.objects.filter(setor=setor)
        if 'responsavel_eletronico' in form.fields:
            form.fields['responsavel_eletronico'].queryset = Tecnicos.objects.filter(setor=setor)

        return form

class EquipamentoDetailView(DetailView):
    model = Equipamento
    template_name = 'equipamento_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipamento = self.get_object()
        context['subcomponentes'] = equipamento.subcomponente_set.all()
        context['linhas'] = Linha.objects.all()
        return context

class EquipamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipamento
    form_class = EquipamentoModelForm
    template_name = 'equipamento_update.html'
    
    def get_success_url(self):
        return reverse_lazy('equipamento_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.arquivo = self.request.FILES.get('arquivo', None)
        return super().form_valid(form)

class EquipamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipamento
    template_name = 'equipamento_delete.html'
    success_url = reverse_lazy('equipamento_list')

class SubcomponenteCreateView(LoginRequiredMixin, CreateView):
    model = Subcomponente
    form_class = SubcomponenteForm
    template_name = 'subcomponente_create.html'

    def get_success_url(self):
        equipamento_pk = self.kwargs['pk']  # Obtém o ID do equipamento dos parâmetros da URL
        return reverse_lazy('equipamento_detail', kwargs={'pk': equipamento_pk})


class SubcomponenteDetailView(LoginRequiredMixin, DetailView):
    model = Subcomponente
    template_name = 'subcomponente_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historico_form'] = HistoricoSubcomponenteForm()
        return context

class SubcomponenteUpdateView(LoginRequiredMixin, UpdateView):
    model = Subcomponente
    form_class = SubcomponenteForm
    template_name = 'subcomponente_update.html'

    def get_success_url(self):
        return reverse_lazy('equipamento_detail', kwargs={'pk': self.object.equipamento.pk})

class SubcomponenteDeleteView(LoginRequiredMixin, DeleteView):
    model = Subcomponente
    template_name = 'subcomponente_delete.html'

    def get_success_url(self):
        return reverse_lazy('equipamento_detail', kwargs={'pk': self.object.equipamento.pk})


class HistoricoSubcomponenteCreateView(LoginRequiredMixin, CreateView):
    model = HistoricoSubcomponente
    form_class = HistoricoSubcomponenteForm
    template_name = 'historico_create.html'

    def form_valid(self, form):
        subcomponente = get_object_or_404(Subcomponente, pk=self.kwargs['pk'])
        form.instance.subcomponente = subcomponente
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('subcomponente_detail', kwargs={'pk': self.kwargs['pk']})

class HistoricoSubcomponenteDetailView(LoginRequiredMixin, DetailView):
    model = HistoricoSubcomponente
    template_name = 'historico_detail.html'
    context_object_name = 'historico'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicione aqui qualquer outro contexto que desejar
        return context
    
class HistoricoSubcomponenteListView(LoginRequiredMixin, ListView):
    model = HistoricoSubcomponente
    template_name = 'historico_subcomponente_list.html'
    context_object_name = 'historico_list'

    def get_queryset(self):
        subcomponente_id = self.kwargs['pk']
        return HistoricoSubcomponente.objects.filter(subcomponente_id=subcomponente_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subcomponente_id'] = self.kwargs['pk']  # Define subcomponente_id no contexto
        return context
