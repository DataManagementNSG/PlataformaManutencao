from django.db import models
from spare.models import Material
from tecnicos.models import Tecnicos
from equipamento.models import Equipamento
from django.contrib.auth.models import User

class Prioridade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Status(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Falhas(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Ordem(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='ordens')
    prioridade = models.ForeignKey(Prioridade, on_delete=models.CASCADE, related_name='ordens')
    falhas = models.ForeignKey(Falhas, on_delete=models.CASCADE, blank=True, null=True, related_name='ordens')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='ordens')
    responsavel = models.ForeignKey(Tecnicos, on_delete=models.CASCADE, related_name='ordens')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    arquivo = models.FileField(upload_to='ordem/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

class MaterialOrdem(models.Model):
    ordem = models.ForeignKey(Ordem, on_delete=models.CASCADE, related_name='materiais')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='materiais_ordem')
    quantidade_utilizada = models.IntegerField()

    def __str__(self):
        return f'{self.material.nome} ({self.quantidade_utilizada})'
