from django import forms
from .models import Outflow

class OutflowForm(forms.ModelForm):
    class Meta:
        model = Outflow
        fields = ['codigo_sap', 'descricao', 'quantidade']
        widgets = {
            'codigo_sap': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'codigo_sap': 'Código SAP',
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
