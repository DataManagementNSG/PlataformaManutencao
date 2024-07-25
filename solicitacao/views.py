from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, View, CreateView, DeleteView, DetailView, UpdateView
from .models import Solicitacao
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from .forms import SolicitacaoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Usuario
from tecnicos.models import Tecnicos
from django.http import JsonResponse
from django.views.generic import View
from dal import autocomplete
from .models import Equipamento
from .models import Solicitacao, Linha, Area, Criticidade, Equipamento


class SolicitacaoListView(LoginRequiredMixin, ListView):
    model = Solicitacao
    template_name = 'listar_solicitacoes.html'
    context_object_name = 'solicitacoes'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        setor = usuario.setor
        solicitacoes = Solicitacao.objects.filter(setor=setor).order_by('data_criacao')

        search_linha = self.request.GET.get('linha')
        search_area = self.request.GET.get('area')

        if search_linha:
            solicitacoes = solicitacoes.filter(linha_id=search_linha)
        if search_area:
            solicitacoes = solicitacoes.filter(area_id=search_area)

        return solicitacoes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        setor = usuario.setor

        # Adicionar linhas e áreas ao contexto
        context['linhas'] = Linha.objects.filter(setor=setor)
        context['areas'] = Area.objects.all()

        # Adicionar parâmetros de busca ao contexto
        context['search_linha'] = self.request.GET.get('linha', '')
        context['search_area'] = self.request.GET.get('area', '')

        # Adicionar a paginação ao contexto
        solicitacoes = context['solicitacoes']
        paginator = Paginator(solicitacoes, self.paginate_by)
        page = self.request.GET.get('page', 1)
        try:
            solicitacoes_paginadas = paginator.page(page)
        except EmptyPage:
            solicitacoes_paginadas = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            solicitacoes_paginadas = paginator.page(1)
        context['solicitacoes'] = solicitacoes_paginadas

        return context

class SolicitacaoCreateView(LoginRequiredMixin, CreateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'criar_solicitacao.html'
    success_url = reverse_lazy('solicitacao_list')

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
        form.fields['linha'].queryset = Linha.objects.filter(setor=setor)
        form.fields['area'].queryset = Area.objects.filter(setor=setor)
        form.fields['equipamento'].queryset = Equipamento.objects.filter(linha__setor=setor)

        return form

class SolicitacaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'editar_solicitacao.html'
    success_url = reverse_lazy('solicitacao_list')

class SolicitacaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Solicitacao
    template_name = 'excluir_solicitacao.html'
    success_url = reverse_lazy('solicitacao_list')

class SolicitacaoDetailView(LoginRequiredMixin, DetailView):
    model = Solicitacao
    template_name = 'detalhes_solicitacao.html'
    context_object_name = 'solicitacao'

class FecharCartaoSolicitacaoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        solicitacao = get_object_or_404(Solicitacao, id=kwargs['solicitacao_id'])
        descricao_trabalho = request.POST.get('descricao_trabalho')
        quem_fechou = request.POST.get('quem_fechou')
        solicitacao.descricao_trabalho = descricao_trabalho
        solicitacao.quem_fechou = quem_fechou
        solicitacao.data_fechamento = timezone.now()
        solicitacao.save()
        return redirect('solicitacao_list')

    def get(self, request, *args, **kwargs):
        solicitacao = get_object_or_404(Solicitacao, id=kwargs['solicitacao_id'])
        return render(request, 'fechar_solicitacao.html', {'solicitacao': solicitacao})

class EquipamentoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Equipamento.objects.all()

        if self.request.user.is_authenticated:
            user = self.request.user
            usuario = get_object_or_404(Usuario, user=user)
            setor = usuario.setor

            # Filtra equipamentos pela linha do setor
            qs = qs.filter(linha__setor=setor)

            # Se o usuário pertence ao setor que deve ver o equipamento, mantenha
            if usuario.setor == setor:  # ou a condição adequada para sua lógica
                pass
            else:
                # Se não pertence ao setor, exclua os equipamentos da linha específica
                qs = qs.exclude(linha__setor=setor)

        return qs