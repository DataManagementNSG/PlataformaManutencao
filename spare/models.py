from django.contrib.auth.models import User
from django.db import models
from accounts.models import Setor
from tecnicos.models import Tecnicos
from django.utils import timezone
from django.core.exceptions import ValidationError
 
# Categorias dos materiais
class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

# Criticidade dos materiais
class Criticidade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

# Cadastrar o tipo de material: Ex: peça, metros e etc.
class Unidade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    codigo_sap = models.CharField(max_length=20, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

class Material(models.Model):
    CRITICIDADE_CHOICES = [
        ('C', 'C'),
        ('B', 'B'),
        ('A', 'A'),
    ]
    quantidade = models.IntegerField(blank=True, null=True)
    quantidade_minima = models.IntegerField(blank=True, null=True)
    quantidade_maxima = models.IntegerField(blank=True, null=True)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True)
    localizacao = models.CharField(max_length=100, blank=True, null=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margem_proximo_minimo = models.IntegerField(blank=True, null=True)
    criticidade = models.CharField(max_length=10, choices=CRITICIDADE_CHOICES, blank=True, null=True)
    responsavel = models.ForeignKey(Tecnicos, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(upload_to='spare/', blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='materiais_criados')
    alterado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='materiais_alterados')
    deletado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='materiais_deletados')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=False)

    def save(self, *args, **kwargs):
        if not self.pk and 'request' in kwargs:
            self.criado_por = kwargs['request'].user
        elif 'request' in kwargs:
            self.alterado_por = kwargs.pop('request').user
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if 'request' in kwargs:
            self.deletado_por = kwargs['request'].user
            self.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nome

    # Cálculo do valor total do item em estoque.
    def valor_total(self):
        if self.quantidade is not None and self.valor_unitario is not None:
            return self.quantidade * self.valor_unitario
        return None

    # Cálculo de quantidade próxima ao nível mínimo.
    def status_quantidade(self):
        if self.quantidade is not None and self.quantidade_minima is not None and self.margem_proximo_minimo is not None:
            if self.quantidade <= self.quantidade_minima:
                return "vermelho"
            elif self.quantidade <= self.quantidade_minima + self.margem_proximo_minimo:
                return "amarelo"
            else:
                return "verde"
        return None