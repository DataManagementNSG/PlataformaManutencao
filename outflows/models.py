from django.db import models
from django.contrib.auth.models import User

class Outflow(models.Model):
    codigo_sap = models.CharField(max_length=9)
    descricao = models.TextField(null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Novo campo

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return self.codigo_sap
    