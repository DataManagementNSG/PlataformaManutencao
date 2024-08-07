from django.db import models
from django.contrib.auth.models import User

# Setores da Empresa como: Temperado, 2DFB, Lehr2, Lehr, BDRV, T.O, BOX.
class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Setor")
    descricao = models.TextField(null=True, blank=True, verbose_name="Descrição")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"

# Funcionários dos Setores Acima.
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, verbose_name="Setor")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
