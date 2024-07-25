from django import forms
from .models import Equipamento, Subcomponente, HistoricoSubcomponente, Linha, Area
from tecnicos.models import Tecnicos

class EquipamentoModelForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        exclude = ['setor']
        fields = '__all__'
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'linha': 'Linha',
            'area': 'Área',
            'criticidade': 'Criticidade',
            'custo_hora_parada': 'Custo por Hora de Parada',
            'responsavel_mecanico': 'Responsável Mecânico',
            'responsavel_eletronico': 'Responsável Eletrônico',
            'arquivo': 'Arquivo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'linha': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'criticidade': forms.Select(attrs={'class': 'form-control'}),
            'custo_hora_parada': forms.NumberInput(attrs={'class': 'form-control'}),
            'responsavel_mecanico': forms.Select(attrs={'class': 'form-control'}),
            'responsavel_eletronico': forms.Select(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            user = request.user
            try:
                setor = user.usuario.setor
            except AttributeError:
                setor = None

            if setor:
                self.fields['linha'].queryset = Linha.objects.filter(setor=setor)
                self.fields['area'].queryset = Area.objects.filter(setor=setor)
                self.fields['responsavel_mecanico'].queryset = Tecnicos.objects.filter(setor=setor)
                self.fields['responsavel_eletronico'].queryset = Tecnicos.objects.filter(setor=setor)

class SubcomponenteForm(forms.ModelForm):
    class Meta:
        model = Subcomponente
        fields = ['nome', 'descricao_subcomponente', 'equipamento', 'linha']
        labels = {
            'nome': 'Nome',
            'descricao_subcomponente': 'Descrição',
            'equipamento': 'Equipamento',
            'linha': 'Linha'
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_subcomponente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'equipamento': forms.Select(attrs={'class': 'form-control'}),
            'linha': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Atualizando o queryset do campo 'equipamento'
        self.fields['equipamento'].queryset = Equipamento.objects.all()
        # Atualizando o queryset do campo 'linha'
        self.fields['linha'].queryset = Linha.objects.all()

    def clean_equipamento(self):
        equipamento = self.cleaned_data.get('equipamento')
        if equipamento and not Equipamento.objects.filter(pk=equipamento.pk).exists():
            raise forms.ValidationError("Por favor, selecione um equipamento válido.")
        return equipamento

class HistoricoSubcomponenteForm(forms.ModelForm):
    class Meta:
        model = HistoricoSubcomponente
        fields = ['data', 'descricao']
        labels = {
            'data': 'Data',
            'descricao': 'Descrição'
        }
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
