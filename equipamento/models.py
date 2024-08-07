from django.db import models
from spare.models import Criticidade
from tecnicos.models import Tecnicos
from accounts.models import Setor

class Linha(models.Model):
    nome = models.CharField(max_length=100)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nome

class Area(models.Model):
    nome = models.CharField(max_length=100)
    setor = models.ManyToManyField(Setor, blank=True)

    def __str__(self):
        return self.nome

class Equipamento(models.Model):
    CRITICIDADE_CHOICES = [
        ('Baixa', 'Baixa'),
        ('Média', 'Média'),
        ('Alta', 'Alta'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    linha = models.ForeignKey(Linha, on_delete=models.CASCADE, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    criticidade = models.CharField(max_length=6, choices=CRITICIDADE_CHOICES, blank=True, null=True)
    custo_hora_parada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    responsavel_mecanico = models.ForeignKey(Tecnicos, on_delete=models.CASCADE, related_name='equipamentos_mecanicos', blank=True, null=True)
    responsavel_eletronico = models.ForeignKey(Tecnicos, on_delete=models.CASCADE, related_name='equipamentos_eletronicos', blank=True, null=True)
    arquivo = models.FileField(upload_to='ativo/', blank=True, null=True)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nome

class Subcomponente(models.Model):
    nome = models.CharField(max_length=100)
    descricao_subcomponente = models.TextField(null=True, blank=True)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, blank=True, null=True)
    linha = models.ForeignKey(Linha, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(upload_to='subcomponente/', blank=True, null=True)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nome

class HistoricoSubcomponente(models.Model):
    subcomponente = models.ForeignKey(Subcomponente, on_delete=models.CASCADE)
    data = models.DateField()
    descricao = models.TextField()

    def __str__(self):
        return f"Histórico de {self.subcomponente.nome} em {self.data}"
