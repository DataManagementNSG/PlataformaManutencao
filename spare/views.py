from spare.models import Material, Categoria, Criticidade
from django.shortcuts import render, get_object_or_404, redirect
from spare.forms import MaterialModelForm, CategoryForm
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from .utils import generate_barcode
from urllib.parse import urlencode
from accounts.models import Usuario
from .forms import UploadExcelForm
from .models import Item
import pandas as pd
from django.http import JsonResponse
from django.contrib import messages 


class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'spare.html'
    context_object_name = 'materials'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        usuario = get_object_or_404(Usuario, user=user)
        materials = Material.objects.filter(setor=usuario.setor).order_by('item__nome_sap')  

        search_item = self.request.GET.get('item')
        search_codigo_sap = self.request.GET.get('codigo_sap')
        search_categoria = self.request.GET.get('categoria')
        search_criticidade = self.request.GET.get('criticidade')
        search_localizacao = self.request.GET.get('localizacao')

        if search_item:
            materials = materials.filter(item__nome_sap__icontains=search_item)
        if search_codigo_sap:
            materials = materials.filter(codigo_sap__icontains=search_codigo_sap)
        if search_categoria:
            materials = materials.filter(categoria__nome=search_categoria)
        if search_criticidade:
            materials = materials.filter(criticidade=search_criticidade)
        if search_localizacao:
            materials = materials.filter(localizacao=search_localizacao)

        return materials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['criticidades'] = Criticidade.objects.all()
        context['categorias'] = Categoria.objects.all()  # Todas as categorias, sem vínculo com setor

        # Armazenar os parâmetros de busca
        context['search_item'] = self.request.GET.get('item', '')
        context['search_codigo_sap'] = self.request.GET.get('codigo_sap', '')
        context['search_categoria'] = self.request.GET.get('categoria', '')
        context['search_criticidade'] = self.request.GET.get('criticidade', '')

        self.request.session['search_item'] = context['search_item']
        self.request.session['search_codigo_sap'] = context['search_codigo_sap']
        self.request.session['search_categoria'] = context['search_categoria']
        self.request.session['search_criticidade'] = context['search_criticidade']
        self.request.session['page_number'] = self.request.GET.get('page', 1)

        paginator = Paginator(context['materials'], self.paginate_by)
        page = self.request.GET.get('page', 1)

        try:
            materials_paginados = paginator.page(page)
        except PageNotAnInteger:
            materials_paginados = paginator.page(1)
        except EmptyPage:
            materials_paginados = paginator.page(paginator.num_pages)

        context['materials'] = materials_paginados

        return context
    
def import_items_from_excel(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                # Verifique se o arquivo é um Excel válido
                if not excel_file.name.endswith(('.xlsx', '.xls')):
                    messages.error(request, 'O arquivo enviado não é um arquivo Excel válido.')
                    return redirect('import_items')

                # Ler o arquivo Excel
                df = pd.read_excel(excel_file)

                # Verifique o conteúdo do DataFrame
                print(df.head())  # Verifique as primeiras linhas do arquivo Excel no console

                # Verificar se as colunas necessárias estão presentes
                required_columns = {'nome', 'codigo_sap', 'descricao'}
                if not required_columns.issubset(df.columns):
                    messages.error(request, 'O arquivo Excel deve conter as colunas: nome, codigo_sap, descricao.')
                    return redirect('import_items')

                imported_count = 0
                updated_count = 0

                # Importar dados para o modelo Item
                for _, row in df.iterrows():
                    codigo_sap = row.get('codigo_sap')
                    nome_sap = row.get('nome')
                    descricao_sap = row.get('descricao')

                    # Verifique se os dados estão corretos
                    print(f"Processando: Código SAP: {codigo_sap}, Nome: {nome_sap}, Descrição: {descricao_sap}")

                    # Validar se os campos obrigatórios não estão vazios
                    if pd.isna(codigo_sap) or pd.isna(nome_sap) or pd.isna(descricao_sap):
                        messages.error(request, f"Linhas com dados inválidos foram encontradas e ignoradas. Verifique o arquivo.")
                        continue

                    # Verificar se o item já existe
                    item, created = Item.objects.get_or_create(
                        codigo_sap=codigo_sap,
                        defaults={'nome_sap': nome_sap, 'descricao_sap': descricao_sap}
                    )

                    if not created:
                        # Verificar se há modificações
                        if item.nome_sap != nome_sap or item.descricao_sap != descricao_sap:
                            item.nome_sap = nome_sap
                            item.descricao_sap = descricao_sap
                            item.save()
                            updated_count += 1
                            print(f"Item {codigo_sap} atualizado.")
                    else:
                        imported_count += 1
                        print(f"Item {codigo_sap} importado.")

                messages.success(request, f'{imported_count} itens importados e {updated_count} itens atualizados com sucesso!')
                return redirect('spare_list')  # Redirecionar para uma lista de itens ou outra página
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao importar o arquivo: {e}')
                print(f"Erro: {e}")  # Verifique o erro no console
    else:
        form = UploadExcelForm()

    return render(request, 'import_items.html', {'form': form})

class NewMaterialCreateView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialModelForm
    template_name = 'new_spare.html'
    success_url = reverse_lazy('spare_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        usuario = Usuario.objects.get(user=self.request.user)
        setor = usuario.setor

        form.instance.setor = setor
        form.instance.criado_por = self.request.user
        form.instance.user = self.request.user

        if not form.instance.item:
            item = Item.objects.filter(codigo_sap=form.instance.codigo_sap).first()
            if item:
                form.instance.item = item
            else:
                form.add_error('codigo_sap', 'Item não encontrado para o código SAP fornecido.')
                return self.form_invalid(form)

        print(f'Item ID no form_valid: {form.instance.item}')

        response = super().form_valid(form)
        material = self.object

        if material.codigo_sap:
            barcode_image = generate_barcode(material.codigo_sap, material.localizacao, material.item.nome_sap)
            material.barcode_image.save(f'{material.codigo_sap}.png', barcode_image)
            material.save()
        else:
            form.add_error('codigo_sap', 'Material não possui código SAP.')
            return self.form_invalid(form)

        return response

    def form_invalid(self, form):
        print(f'Erros no formulário: {form.errors}')
        return super().form_invalid(form)

def get_item_by_codigo_sap(request):
    codigo_sap = request.GET.get('codigo_sap', None)
    data = {}
    if codigo_sap:
        try:
            item = Item.objects.get(codigo_sap=codigo_sap)
            data = {
                'id': item.id,
                'nome': item.nome_sap,
            }
        except Item.DoesNotExist:
            data = {'error': 'Item não encontrado'}
        except Exception as e:
            data = {'error': str(e)}
    return JsonResponse(data)

class MaterialDetailView(LoginRequiredMixin, DetailView):
    model = Material
    template_name = 'spare_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recupere os parâmetros de busca e o número da página da sessão
        search_nome = self.request.session.get('search_nome', '')
        search_codigo_sap = self.request.session.get('search_codigo_sap', '')
        search_categoria = self.request.session.get('search_categoria', '')
        page_number = self.request.session.get('page_number', 1)

        # Construa o dicionário de parâmetros de consulta
        query_params = {
            'page': page_number,
            'nome': search_nome,
            'codigo_sap': search_codigo_sap,
            'categoria': search_categoria,
        }

        # Remova parâmetros vazios
        query_params = {k: v for k, v in query_params.items() if v}

        # Construa a URL de volta com os parâmetros de busca e o número da página
        context['back_url'] = f"{reverse('spare_list')}?{urlencode(query_params)}"

        return context

class MaterialUpdateView(LoginRequiredMixin, UpdateView):
    model = Material
    form_class = MaterialModelForm
    template_name = 'spare_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse('spare_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Verifica se o barcode_image foi enviado e o define
        barcode_image = self.request.FILES.get('barcode_image', None)
        if barcode_image:
            form.instance.barcode_image = barcode_image
        form.instance.alterado_por = self.request.user
        
        response = super().form_valid(form)
        
        # Adicione prints para depuração
        print('Item:', form.instance.item)
        print('Barcode Image:', form.instance.barcode_image)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_nome = self.request.session.get('search_nome', '')
        search_codigo_sap = self.request.session.get('search_codigo_sap', '')
        search_categoria = self.request.session.get('search_categoria', '')
        page_number = self.request.session.get('page_number', 1)

        context['back_url'] = f"{reverse('spare_list')}?page={page_number}&nome={search_nome}&codigo_sap={search_codigo_sap}&categoria={search_categoria}"
        return context

class MaterialDeleteView(LoginRequiredMixin, DeleteView):
    model = Material
    template_name = 'spare_delete.html'
    success_url = reverse_lazy('spare_list')

    def delete(self, request, *args, **kwargs):
        material = self.get_object()
        material.deletado_por = request.user
        material.save()
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_nome = self.request.session.get('search_nome', '')
        search_codigo_sap = self.request.session.get('search_codigo_sap', '')
        search_categoria = self.request.session.get('search_categoria', '')
        page_number = self.request.session.get('page_number', 1)

        context['back_url'] = f"{reverse('spare_list')}?page={page_number}&nome={search_nome}&codigo_sap={search_codigo_sap}&categoria={search_categoria}"
        return context

class MaterialEsgotadoView(LoginRequiredMixin, View):
    template_name = 'spare_esgotado.html'

    def get(self, request, *args, **kwargs):
        materials_esgotados = Material.objects.filter(quantidade=0)
        return render(request, self.template_name, {'esgotados': materials_esgotados})
    
class CategoryListView(ListView):
    model = Categoria
    template_name = 'category_list.html'  # Template para exibir a lista
    context_object_name = 'categorias'

# Criação de nova categoria
class CategoryCreateView(CreateView):
    model = Categoria
    form_class = CategoryForm  # Define o formulário com validação
    template_name = 'category_create.html'
    success_url = reverse_lazy('category_list')