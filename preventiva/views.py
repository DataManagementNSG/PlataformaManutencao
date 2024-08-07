from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import F, Count
from django.utils import timezone
from openpyxl import Workbook
from django.contrib.auth.models import User
import pandas as pd
from datetime import datetime
from spare.models import Material
from tecnicos.models import Tecnicos
from preventiva.models import Preventiva, Atividade
from solicitacao.models import Solicitacao
from .forms import UploadFileForm, PreventivaForm
from .utils import vincular_atividades
from accounts.models import Setor
from django.utils.dateparse import parse_datetime, parse_date
from math import isnan


class PreventivaFechadaListView(ListView):
    model = Preventiva
    template_name = 'preventiva_fechada_list.html'
    context_object_name = 'preventivas'

    def get_queryset(self):
        return Preventiva.objects.filter(status_preventiva=False)

class PreventivaCreateView(CreateView):
    model = Preventiva
    form_class = PreventivaForm
    template_name = 'criar_preventiva.html'
    success_url = reverse_lazy('preventiva_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        vincular_atividades(self.object)
        return response

class TecnicosDetailView(DetailView):
    model = Preventiva
    template_name = 'responsavel_detail.html'
    context_object_name = 'responsavel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responsavel = self.get_object()
        
        # Filtrar todas as preventivas relacionadas ao responsável
        preventivas = Preventiva.objects.filter(
            responsavel=responsavel,
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
        
        # Adicione também a lista de preventivas para ser exibida na tabela
        context['preventivas'] = preventivas
        context['today'] = today  # Adiciona a data atual ao contexto
        
        return context

class PreventivaDetailView(DetailView):
    model = Preventiva
    template_name = 'preventiva_detail.html'
    context_object_name = 'preventiva'

class PreventivaUpdateView(UpdateView):
    model = Preventiva
    form_class = PreventivaForm
    template_name = 'editar_preventiva.html'
    success_url = reverse_lazy('preventiva_list')

class PreventivaDeleteView(DeleteView):
    model = Preventiva
    template_name = 'confirmar_exclusao.html'
    success_url = reverse_lazy('preventiva_list')

# Função para gerar relatório em Excel
def relatorio_excel(request):
    preventivas = Preventiva.objects.filter(status_preventiva=False)
    wb = Workbook()
    ws = wb.active
    ws.append(['Ordem', 'Texto Breve', 'Data de Início', 'Data de Fim', 'Tempo de Execução', 'Comentários', 'Centro de Trabalho Responsável'])

    for preventiva in preventivas:
        ws.append([
            preventiva.ordem,
            preventiva.texto_breve,
            preventiva.data_inicio,
            preventiva.data_fim,
            preventiva.tempo_execucao,
            preventiva.comentarios,
            preventiva.centro_trabalho_responsavel
        ])

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="relatorio_preventivas_fechadas.xlsx"'
    wb.save(response)
    return response

# Atualizar status SAP via POST
@require_POST
def atualizar_status_sap(request):
    preventiva_id = request.POST.get('preventiva_id')
    is_checked = request.POST.get('isChecked') == 'true'

    try:
        preventiva = Preventiva.objects.get(pk=preventiva_id)
        preventiva.lancado_no_sap = is_checked
        preventiva.save()
        return JsonResponse({'message': 'Status atualizado com sucesso.'})
    except Preventiva.DoesNotExist:
        return JsonResponse({'error': 'Preventiva não encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Exibir materiais que estão acabando pelos responsáveis
def materiais_por_responsavel(request, responsavel_id):
    responsavel = get_object_or_404(Tecnicos, id=responsavel_id)
    materiais = Material.objects.filter(responsavel=responsavel, quantidade__lte=F('quantidade_minima'))
    return render(request, 'materiais_por_responsavel.html', {'responsavel': responsavel, 'materiais': materiais})

# Solicitações por técnico
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

# Função auxiliar para parse de datas
def parse_date(date_value):
    if pd.notna(date_value):
        if isinstance(date_value, pd.Timestamp):
            return date_value.strftime('%Y-%m-%d')
        elif isinstance(date_value, str):
            try_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %I:%M %p',
                '%d/%m/%Y %H:%M:%S',
                '%d-%m-%Y %H:%M:%S'
            ]
            for fmt in try_formats:
                try:
                    return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
    return None

# Função para upload de arquivos e importação de dados
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file)

                # Obter o setor do usuário logado
                setor_usuario = request.user.usuario.setor

                for _, row in df.iterrows():
                    def safe_parse_date(date_str):
                        if pd.notna(date_str):
                            try:
                                # Verifica se é uma data ou datetime
                                if isinstance(date_str, str):
                                    return parse_datetime(date_str) or parse_date(date_str)
                                return date_str
                            except ValueError:
                                return None
                        return None

                    liberacao_real = safe_parse_date(row.get('Liberação real'))
                    data_base_inic = safe_parse_date(row.get('Data-base iníc.'))
                    data_base_fim = safe_parse_date(row.get('Data-base fim'))
                    inic_real_hr = safe_parse_date(row.get('InícReal hr.'))
                    fim_real_hr = safe_parse_date(row.get('Fim real hora'))

                    posto_trabalho = row.get('CenTrab respon.')
                    responsavel = Tecnicos.objects.filter(centro_trabalho_responsavel=posto_trabalho).first()

                    setor_nome = row.get('Setor', setor_usuario.nome)
                    setor = Setor.objects.filter(nome__iexact=setor_nome).first() or setor_usuario

                    # Verificar se o usuário responsável existe
                    criado_por_nome = row.get('Criado por')
                    # Aqui, `criado_por_nome` é a string esperada para o CharField
                    # Em vez de buscar um objeto User, vamos usar o nome diretamente
                    criado_por = criado_por_nome if criado_por_nome else request.user.username

                    if responsavel:
                        preventiva, created = Preventiva.objects.update_or_create(
                            ordem=row.get('Ordem'),
                            defaults={
                                'tipo_ordem': row.get('Tipo de ordem', ''),
                                'loc_instalacao': row.get('Loc.instalação', ''),
                                'denominacao': row.get('Denominação', ''),
                                'nota': row.get('Nota', 'Default note value'),
                                'texto_breve': row.get('Texto breve', ''),
                                'liberacao_real': liberacao_real,
                                'data_base_inic': data_base_inic,
                                'data_base_fim': data_base_fim,
                                'inic_real_hr': inic_real_hr,
                                'fim_real_hr': fim_real_hr,
                                'criado_por': criado_por,
                                'centro_trabalho_responsavel': posto_trabalho,
                                'centro_custo': row.get('Centro custo', ''),
                                'total_real': row.get('Total real', 0),
                                'status_sistema': row.get('Status sistema', ''),
                                'data_inicio': row.get('Data Início', None),
                                'data_fim': row.get('Data Fim', None),
                                'tempo_execucao': row.get('Tempo Execução', ''),
                                'comentarios': row.get('Comentários', ''),
                                'responsavel': responsavel,
                                'setor': setor
                            }
                        )

                        atividades = Atividade.objects.filter(nome__iexact=row.get('Texto breve'))
                        if atividades.exists():
                            preventiva.atividades.set(atividades)
                            print(f"Atividades vinculadas: {atividades} à preventiva {preventiva}")
                        else:
                            print(f"Nenhuma atividade encontrada para o texto breve: {row.get('Texto breve')}")
                    else:
                        print(f"Responsável não encontrado para o posto de trabalho: {posto_trabalho}")

                messages.success(request, 'Dados importados com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao importar dados: {e}')
            return redirect('tecnicos_list')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

# Listagem de preventivas abertas
def preventiva_list(request):
    # Obter o setor do usuário logado
    setor_usuario = request.user.usuario.setor
    
    # Filtrar preventivas pelo setor do usuário
    preventivas = Preventiva.objects.filter(setor=setor_usuario)

    return render(request, 'preventiva_list.html', {'preventivas': preventivas})

# Detalhe de preventiva
def atividade_detail(request, pk):
    preventiva = get_object_or_404(Preventiva, pk=pk)
    return render(request, 'atividade_detail.html', {'object': preventiva})

# Fechar preventiva
def fechar_preventiva_view(request, pk):
    preventiva = get_object_or_404(Preventiva, pk=pk)

    if request.method == 'POST':
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        tempo_execucao = request.POST.get('tempo_execucao')
        comentarios = request.POST.get('comentarios')

        preventiva.data_inicio = data_inicio
        preventiva.data_fim = data_fim
        preventiva.tempo_execucao = tempo_execucao
        preventiva.comentarios = comentarios
        preventiva.status_preventiva = False
        preventiva.save()

        messages.success(request, 'Preventiva fechada com sucesso!')
        return redirect('preventiva_list')

    return render(request, 'fechar_preventiva.html', {'preventiva': preventiva})

# Desvio por responsável
def desvios_por_responsavel(request):
    desvios = Preventiva.objects.filter(tempo_execucao__gt=F('tempo_estimado'))
    responsaveis = Tecnicos.objects.filter(id__in=desvios.values('responsavel_id')).distinct()
    return render(request, 'desvios_por_responsavel.html', {'desvios': desvios, 'responsaveis': responsaveis})

# Manutenção por equipamento
def manutencao_por_equipamento(request):
    equipamentos = Preventiva.objects.values('equipamento').annotate(total_manutencao=Count('id')).order_by('-total_manutencao')
    return render(request, 'manutencao_por_equipamento.html', {'equipamentos': equipamentos})

# Visualizar preventivas por período
def preventivas_por_periodo(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        preventivas = Preventiva.objects.filter(data_inicio__gte=start_date, data_fim__lte=end_date)
    else:
        preventivas = Preventiva.objects.all()

    return render(request, 'preventivas_por_periodo.html', {'preventivas': preventivas})

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