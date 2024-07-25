# forms.py
from django import forms
from .models import Tecnicos

class TecnicosForm(forms.ModelForm):
    class Meta:
        model = Tecnicos
        fields = ['nome', 'email', 'centro_trabalho_responsavel', 'especialidade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'centro_trabalho_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome',
            'email': 'Email',
            'centro_trabalho_responsavel': 'Centro de Trabalho',
            'especialidade': 'Especialidade',
        }
