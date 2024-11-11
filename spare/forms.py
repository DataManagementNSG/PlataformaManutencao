from django import forms
from .models import Material, Categoria, Item
from tecnicos.models import Tecnicos
from django.core.exceptions import ValidationError

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Escolha o arquivo Excel')

class MaterialModelForm(forms.ModelForm):
    class Meta:
        model = Material
        exclude = ['user', 'setor', 'criado_por', 'alterado_por', 'deletado_por', 'barcode_image']
        labels = {
            'codigo_sap': 'Código SAP',
            'item': 'Nome do Item SAP',
            'apelido_linha': 'Nome (Linha)',
            'descricao_fornecedor': 'Descrição Fornecedor',
            'quantidade': 'Quantidade Atual',
            'quantidade_minima': 'Quantidade Mínima',
            'quantidade_maxima': 'Quantidade Máxima',
            'unidade': 'Unidade',
            'categoria': 'Categoria',
            'localizacao': 'Localização',
            'valor_unitario': 'Valor Unitário',
            'margem_proximo_minimo': 'Margem Próxima ao Nível',
            'criticidade': 'Criticidade',
            'responsavel': 'Responsável',
            'foto': 'Foto',
        }
        widgets = {
            'codigo_sap': forms.TextInput(attrs={'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'apelido_linha': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'descricao_fornecedor': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'margem_proximo_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'criticidade': forms.Select(attrs={'class': 'form-control'}),
            'responsavel': forms.Select(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control-file'}),
            'barcode_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request:
            user = self.request.user
            if hasattr(user, 'usuario'):
                # Filtrando o queryset do campo 'responsavel' com base no setor do usuário
                self.fields['responsavel'].queryset = Tecnicos.objects.filter(setor=user.usuario.setor)
                
                # Filtrando o queryset do campo 'categoria' com base no setor do usuário
        self.fields['categoria'].queryset = Categoria.objects.all()


    def clean_criticidade(self):
        criticidade = self.cleaned_data.get('criticidade')
        if criticidade not in ['A', 'B', 'C']:
            raise forms.ValidationError('Faça uma escolha válida. A não é uma das escolhas disponíveis.')
        return criticidade

    def clean_item(self):
        item = self.cleaned_data.get('item')
        if not item:
            codigo_sap = self.cleaned_data.get('codigo_sap')
            item = Item.objects.filter(codigo_sap=codigo_sap).first()
        if not item:
            raise forms.ValidationError('O Nome do Item SAP é obrigatório.')
        return item

    def clean_codigo_sap(self):
        codigo_sap = self.cleaned_data.get('codigo_sap')
        setor = self.request.user.usuario.setor

        # Verificar se o código SAP já existe no setor, mas ignorar o registro atual
        if Material.objects.filter(codigo_sap=codigo_sap, setor=setor).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este código SAP já está cadastrado no setor.")

        return codigo_sap

    def save(self, commit=True):
        # Atribuir o item com base no código SAP antes de salvar
        self.instance.item = self.cleaned_data.get('item')
        if not self.instance.item and self.instance.codigo_sap:
            item = Item.objects.filter(codigo_sap=self.instance.codigo_sap).first()
            if item:
                self.instance.item = item
        return super().save(commit=commit)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        labels = {
            'nome': 'Nome da Categoria',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if Categoria.objects.filter(nome__iexact=nome).exists():
            raise forms.ValidationError("Essa categoria já existe. Por favor, insira um nome único.")
        return nome