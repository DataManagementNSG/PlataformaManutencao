from dal import autocomplete
from django import forms
from .models import Solicitacao, Equipamento

class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = [
            'autor', 'linha', 'area', 'criticidade', 'equipamento', 'tipo_problema', 
            'componente', 'turno', 'opcoes_checklist', 'descricao', 
        ]
        labels = { 
            'autor': 'Autor',
            'linha': 'Linha',
            'area': 'Área',
            'criticidade': 'Criticidade',
            'equipamento': 'Equipamento',
            'tipo_problema': 'Tipo de Problema',
            'componente': 'Componente',
            'turno': 'Turno',
            'opcoes_checklist': 'Checklist',
            'descricao': 'Descrição',
        }
        widgets = {
            'autor': forms.TextInput(attrs={'class': 'form-control'}), 
            'linha': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'criticidade': forms.Select(attrs={'class': 'form-control'}),
            'equipamento': autocomplete.ModelSelect2(
                url='equipamento-autocomplete',
                forward=['linha', 'area'],
                attrs={'class': 'form-control'}
            ),
            'tipo_problema': forms.Select(attrs={'class': 'form-control'}),
            'componente': forms.TextInput(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-control'}),
            'opcoes_checklist': forms.CheckboxSelectMultiple(),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }