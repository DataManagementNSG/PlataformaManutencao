from django.shortcuts import render, redirect
from django.db.models import Sum
from preventiva.models import Preventiva, Tecnicos
from spare.models import Material, Categoria
from accounts.models import Setor, Usuario
from ai.models import AIResult
from django.http import JsonResponse
from ai.agent import SGEAgent

def get_ai_result(request):
    if request.method == "GET":
        ai_result_obj = AIResult.objects.order_by('-created_at').first()
        if ai_result_obj:
            return JsonResponse({'status': 'success', 'result': ai_result_obj.result})
        else:
            return JsonResponse({'status': 'error', 'message': 'Nenhum resultado disponível.'})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'})

def invoke_agent(request):
    if request.method == "POST":
        user = request.user
        agent = SGEAgent(user=user)
        try:
            agent.invoke()
            return JsonResponse({'status': 'success', 'message': 'Agente invocado com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'})

def home(request):
    user = request.user

    # Verifica se o usuário está autenticado
    if not user.is_authenticated:
        return redirect('login')

    # Obtém o nome do setor do usuário logado
    setor_nome = user.usuario.setor.nome.strip()

    # Dicionário de mapeamento para o nome do setor exibido
    sector_names = {
        '2DFB': 'Manutenção 2DFB',
        'LEHR 1': 'Manutenção LEHR 1',
        'LEHR 2': 'Manutenção LEHR 2',
        'BDRV': 'Manutenção BDRV',
        'APBT/BDR': 'Manutenção APBT/BDR'
    }

    sector_name = sector_names.get(setor_nome, "Manutenção Desconhecida")

    try:
        # Encontra o setor do usuário
        setor_usuario = Setor.objects.get(nome=setor_nome)
    except Setor.DoesNotExist:
        setor_usuario = None

    tecnicos = []
    labels_preventivas = []
    percent_abertas = []
    percent_fechadas = []
    total_spare_parts = 0
    dados_grafico_categorias = []

    if setor_usuario:
        # Filtra técnicos do setor
        responsaveis = Tecnicos.objects.filter(setor=setor_usuario)

        for responsavel in responsaveis:
            # Dados de preventivas por técnico
            total_preventivas = Preventiva.objects.filter(responsavel=responsavel).count()
            if total_preventivas > 0:
                preventivas_abertas = Preventiva.objects.filter(
                    responsavel=responsavel, status_preventiva=True
                ).count()
                preventivas_fechadas = Preventiva.objects.filter(
                    responsavel=responsavel, status_preventiva=False
                ).count()

                percent_abertas.append((preventivas_abertas / total_preventivas) * 100)
                percent_fechadas.append((preventivas_fechadas / total_preventivas) * 100)
            else:
                percent_abertas.append(0)
                percent_fechadas.append(0)

            labels_preventivas.append(responsavel.nome)

            # Dados de materiais vinculados ao técnico
            materiais_ok = Material.objects.filter(
                responsavel=responsavel, quantidade__gt=5
            ).count()
            materiais_proximo_min = Material.objects.filter(
                responsavel=responsavel, quantidade__lte=5, quantidade__gt=0
            ).count()
            materiais_minimo = Material.objects.filter(
                responsavel=responsavel, quantidade=0
            ).count()

            tecnicos.append({
                "nome": responsavel.nome,
                "materiais_ok": materiais_ok,
                "materiais_proximo_min": materiais_proximo_min,
                "materiais_minimo": materiais_minimo,
            })

        # Dados de materiais totais do setor
        total_spare_parts = Material.objects.filter(setor=setor_usuario).aggregate(
            total=Sum('quantidade')
        )['total'] or 0

        # Dados para gráfico de categorias
        categorias = Categoria.objects.all()
        for categoria in categorias:
            quantidade_materiais = Material.objects.filter(
                categoria=categoria, setor=setor_usuario
            ).count()
            dados_grafico_categorias.append({
                'nome': categoria.nome,
                'quantidade': quantidade_materiais,
            })

    # Prepara o contexto para o template
    context = {
        'sector_name': sector_name,
        'labels_preventivas': labels_preventivas,
        'percent_abertas': percent_abertas,
        'percent_fechadas': percent_fechadas,
        'total_spare_parts': total_spare_parts,
        'dados_grafico_categorias': dados_grafico_categorias,
        'tecnicos': tecnicos,
    }

    return render(request, 'dashboard.html', context)