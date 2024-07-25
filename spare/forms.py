from django import forms
from .models import Material
from tecnicos.models import Tecnicos

class MaterialModelForm(forms.ModelForm):
    class Meta:
        model = Material
        exclude = ['user', 'setor', 'criado_por', 'alterado_por', 'deletado_por']  # Excluir os campos 'user', 'setor', 'criado_por', 'alterado_por' e 'deletado_por' do formulário.
        labels = {
            'nome': 'Nome',
            'codigo_sap': 'Código SAP',
            'descricao': 'Descrição',
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
            'imagem': 'Imagem',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_sap': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
            'imagem': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request:
            user = self.request.user
            self.fields['responsavel'].queryset = Tecnicos.objects.filter(setor=user.usuario.setor)
