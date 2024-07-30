from django import forms
from .models import Material
from tecnicos.models import Tecnicos

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Escolha o arquivo Excel')

class MaterialModelForm(forms.ModelForm):
    class Meta:
        model = Material
        exclude = ['user', 'setor', 'criado_por', 'alterado_por', 'deletado_por']
        labels = {
            'codigo_sap': 'Código SAP',
            'item': 'Nome do Item',
            'quantidade': 'Quantidade',
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
            'barcode_image': 'Imagem do Código de Barras',
        }
        widgets = {
            'codigo_sap': forms.TextInput(attrs={'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-control'}),  # Ajustado para Select
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
                self.fields['responsavel'].queryset = Tecnicos.objects.filter(setor=user.usuario.setor)

    def clean_criticidade(self):
        criticidade = self.cleaned_data.get('criticidade')
        if criticidade not in ['A', 'B', 'C']:
            raise forms.ValidationError('Faça uma escolha válida. A não é uma das escolhas disponíveis.')
        return criticidade
