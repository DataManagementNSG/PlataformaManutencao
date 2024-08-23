from django.shortcuts import render, redirect
from django.db.models import Sum
from preventiva.models import Preventiva, Tecnicos
from spare.models import Material, Categoria
from accounts.models import Setor  # Certifique-se de importar o modelo Setor

def home(request):
    user = request.user
    
    # Verifica se o usuário está autenticado
    if not user.is_authenticated:
        return redirect('login')  # Redireciona para a página de login se não estiver logado

    # Obtém o nome do setor do usuário logado
    setor_nome = user.usuario.setor.nome.strip()  # Acessa o campo 'nome' do setor e remove espaços extras

    # Encontra o objeto Setor correspondente ao nome
    try:
        setor_usuario = Setor.objects.get(nome=setor_nome)
    except Setor.DoesNotExist:
        setor_usuario = None

    # Dicionário de mapeamento para o nome do setor que será exibido
    sector_names = {
        '2DFB': 'Manutenção 2DFB',
        'LEHR 1': 'Manutenção LEHR 1',
        'LEHR 2': 'Manutenção LEHR 2',
        'BDRV': 'Manutenção BDRV',
        'APBT/BDR': 'Manutenção APBT/BDR'
    }

    # Obtém o nome do setor com base no dicionário, ou retorna 'Manutenção Desconhecida' se não encontrar
    sector_name = sector_names.get(setor_nome, "Manutenção Desconhecida")

    # Verifica se o setor foi encontrado antes de prosseguir
    if setor_usuario:
        # Filtra os técnicos e preventivas pelo setor do usuário logado
        responsaveis = Tecnicos.objects.filter(setor=setor_usuario)

        labels_preventivas = []
        percent_abertas = []
        percent_fechadas = []

        for responsavel in responsaveis:
            total_preventivas = Preventiva.objects.filter(responsavel=responsavel).count()
            if total_preventivas > 0:
                preventivas_abertas = Preventiva.objects.filter(responsavel=responsavel, status_preventiva=True).count()
                preventivas_fechadas = Preventiva.objects.filter(responsavel=responsavel, status_preventiva=False).count()

                percent_abertas.append((preventivas_abertas / total_preventivas) * 100)
                percent_fechadas.append((preventivas_fechadas / total_preventivas) * 100)
            else:
                percent_abertas.append(0)
                percent_fechadas.append(0)
            
            labels_preventivas.append(responsavel.nome)

        # Calcula a quantidade total de materiais para o setor do usuário
        total_spare_parts = Material.objects.filter(setor=setor_usuario).aggregate(total=Sum('quantidade'))['total'] or 0

        # Obtém as categorias e prepara os dados para o gráfico de categorias
        categorias = Categoria.objects.filter(setor=setor_usuario)
        dados_grafico_categorias = []
        for categoria in categorias:
            quantidade_materiais = Material.objects.filter(categoria=categoria).count()
            dados_grafico_categorias.append({
                'nome': categoria.nome,
                'quantidade': quantidade_materiais,
            })
    else:
        # Se o setor não for encontrado, define valores padrão ou lida com o erro de forma adequada
        labels_preventivas = []
        percent_abertas = []
        percent_fechadas = []
        total_spare_parts = 0
        dados_grafico_categorias = []

    # Prepara o contexto para o template
    context = {
        'sector_name': sector_name,  # Passa o nome do setor para o template
        'labels_preventivas': labels_preventivas,
        'percent_abertas': percent_abertas,
        'percent_fechadas': percent_fechadas,
        'total_spare_parts': total_spare_parts,
        'dados_grafico_categorias': dados_grafico_categorias,
    }

    return render(request, 'dashboard.html', context)
