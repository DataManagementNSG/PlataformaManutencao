from spare.models import Material, Categoria
from django.shortcuts import render, get_object_or_404, redirect
from spare.forms import MaterialModelForm
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from .utils import generate_barcode
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
        materials = Material.objects.filter(setor=usuario.setor).order_by('item__nome')  # Ajustado para 'item__nome'

        search_item = self.request.GET.get('item')
        search_codigo_sap = self.request.GET.get('codigo_sap')
        search_categoria = self.request.GET.get('categoria')

        if search_item:
            materials = materials.filter(item__nome__icontains=search_item)
        if search_codigo_sap:
            materials = materials.filter(codigo_sap__icontains=search_codigo_sap)
        if search_categoria:
            materials = materials.filter(categoria__nome=search_categoria)

        return materials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()

        context['search_item'] = self.request.GET.get('item', '')
        context['search_codigo_sap'] = self.request.GET.get('codigo_sap', '')
        context['search_categoria'] = self.request.GET.get('categoria', '')

        self.request.session['search_item'] = context['search_item']
        self.request.session['search_codigo_sap'] = context['search_codigo_sap']
        self.request.session['search_categoria'] = context['search_categoria']
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
                # Ler o arquivo Excel
                df = pd.read_excel(excel_file)

                # Importar dados para o modelo Item
                for _, row in df.iterrows():
                    Item.objects.create(
                        nome=row.get('nome'),
                        codigo_sap=row.get('codigo_sap'),
                        descricao=row.get('descricao')
                    )

                messages.success(request, 'Itens importados com sucesso!')
                return redirect('item_list')  # Redirecionar para uma lista de itens ou outra página
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao importar o arquivo: {e}')
    else:
        form = UploadExcelForm()

    return render(request, 'import_items.html', {'form': form})

class NewMaterialCreateView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialModelForm
    template_name = 'new_spare.html'
    success_url = reverse_lazy('spare_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  # Correto
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        usuario = Usuario.objects.get(user=self.request.user)
        setor = usuario.setor

        form.instance.setor = setor
        form.instance.criado_por = self.request.user
        form.instance.user = self.request.user

        response = super().form_valid(form)  # Correto
        material = self.object

        if material.codigo_sap:
            barcode_image = generate_barcode(material.codigo_sap)
            material.barcode_image.save(f'{material.codigo_sap}.png', barcode_image)
            material.save()
        else:
            return HttpResponse("Material não possui código SAP", status=400)

        return response

def get_item_by_codigo_sap(request):
    codigo_sap = request.GET.get('codigo_sap', None)
    data = {}
    if codigo_sap:
        try:
            item = Item.objects.get(codigo_sap=codigo_sap)
            data = {
                'id': item.id,
                'nome': item.nome,
            }
        except Item.DoesNotExist:
            data = {'error': 'Item não encontrado'}
    return JsonResponse(data)


class MaterialDetailView(LoginRequiredMixin, DetailView):
    model = Material
    template_name = 'spare_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_nome = self.request.session.get('search_nome', '')
        search_codigo_sap = self.request.session.get('search_codigo_sap', '')
        search_categoria = self.request.session.get('search_categoria', '')
        page_number = self.request.session.get('page_number', 1)

        context['back_url'] = f"{reverse('spare_list')}?page={page_number}&nome={search_nome}&codigo_sap={search_codigo_sap}&categoria={search_categoria}"
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
        form.instance.imagem = self.request.FILES.get('imagem', None)
        form.instance.alterado_por = self.request.user
        return super().form_valid(form)

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
