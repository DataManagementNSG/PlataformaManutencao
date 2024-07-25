from django import forms
from .models import Ordem, MaterialOrdem, User, Equipamento
from accounts.models import Usuario
from tecnicos.models import Tecnicos

class OrdemModelForm(forms.ModelForm):
    class Meta:
        model = Ordem
        exclude = ['user']
        fields = '__all__'
        labels = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'status': 'Status',
            'prioridade': 'Prioridade',
            'falhas': 'Falhas',
            'equipamento': 'Equipamento',
            'responsavel': 'Responsável',
            'arquivo': 'Arquivo',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o título da ordem'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva a ordem'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'falhas': forms.Select(attrs={'class': 'form-control'}),
            'equipamento': forms.Select(attrs={'class': 'form-control'}),
            'responsavel': forms.Select(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            try:
                usuario = user.usuario
                setor = usuario.setor
                self.fields['responsavel'].queryset = Tecnicos.objects.filter(setor=user.usuario.setor)
                self.fields['equipamento'].queryset = Equipamento.objects.filter(setor=setor)
            except Usuario.DoesNotExist:
                self.fields['responsavel'].queryset = User.objects.none()
                self.fields['equipamento'].queryset = Equipamento.objects.none()

class MaterialOrdemModelForm(forms.ModelForm):
    class Meta:
        model = MaterialOrdem
        fields = ['material', 'quantidade_utilizada']
        labels = {
            'material': 'Material',
            'quantidade_utilizada': 'Quantidade Utilizada',
        }
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_utilizada': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean_quantidade_utilizada(self):
        quantidade_utilizada = self.cleaned_data.get('quantidade_utilizada')
        if quantidade_utilizada <= 0:
            raise forms.ValidationError("A quantidade utilizada deve ser maior que zero.")
        return quantidade_utilizada
