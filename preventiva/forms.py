from django import forms
from .models import Preventiva
from django.contrib.auth.models import User  # Se necessário para o campo `criado_por`

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Selecione a planilha Excel', widget=forms.FileInput(attrs={'class': 'form-control-file'}))

class FecharPreventivaForm(forms.ModelForm):
    class Meta:
        model = Preventiva
        fields = ['data_inicio', 'data_fim', 'tempo_execucao', 'comentarios']
        labels = {
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim',
            'tempo_execucao': 'Tempo de Execução',
            'comentarios': 'Comentários',
        }
        widgets = {
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tempo_execucao': forms.TextInput(attrs={'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PreventivaForm(forms.ModelForm):
    criado_por = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = Preventiva
        fields = [
            'tipo_ordem', 'loc_instalacao', 'denominacao', 'nota', 'ordem',
            'texto_breve', 'liberacao_real', 'data_base_inic', 'data_base_fim',
            'inic_real_hr', 'fim_real_hr', 'criado_por', 'centro_trabalho_responsavel',
            'centro_custo', 'total_real', 'status_sistema', 'data_inicio', 'data_fim',
            'tempo_execucao', 'comentarios', 'setor'
        ]
        widgets = {
            'tipo_ordem': forms.TextInput(attrs={'class': 'form-control'}),
            'loc_instalacao': forms.TextInput(attrs={'class': 'form-control'}),
            'denominacao': forms.TextInput(attrs={'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'class': 'form-control'}),
            'ordem': forms.TextInput(attrs={'class': 'form-control'}),
            'texto_breve': forms.TextInput(attrs={'class': 'form-control'}),
            'liberacao_real': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_base_inic': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_base_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inic_real_hr': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fim_real_hr': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'centro_trabalho_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'centro_custo': forms.TextInput(attrs={'class': 'form-control'}),
            'total_real': forms.NumberInput(attrs={'class': 'form-control'}),
            'status_sistema': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tempo_execucao': forms.TextInput(attrs={'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control'}),
            'setor': forms.Select(attrs={'class': 'form-control'}),
        }