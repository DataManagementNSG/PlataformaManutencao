from django.contrib.auth.models import User
from django.db import models
from accounts.models import Setor

class Tecnicos(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, default='')
    centro_trabalho_responsavel = models.CharField(max_length=100, blank=True, null=True)
    especialidade = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, null=True, blank=True)  # Temporariamente opcional

    def __str__(self):
        return self.nome