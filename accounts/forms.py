from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Usuario, Setor

class CustomUserCreationForm(UserCreationForm):
    setor = forms.ModelChoiceField(queryset=Setor.objects.all(), empty_label="Selecione o setor", widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

        labels = {
            'username': 'Nome de Usuário',
            'setor': 'Setor',
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'setor': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        setor = self.cleaned_data['setor']

        if commit:
            user.save()
            Usuario.objects.create(user=user, setor=setor)

        return user
