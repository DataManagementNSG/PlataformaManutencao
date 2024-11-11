from django.contrib.auth.models import User
from django.db import models
from accounts.models import Setor
from tecnicos.models import Tecnicos

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Criticidade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Unidade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome_sap = models.CharField(max_length=100, blank=True, null=True)
    codigo_sap = models.CharField(max_length=20, blank=True, null=True)
    descricao_sap = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome_sap if self.nome_sap else "Sem Nome"

class Material(models.Model):
    CRITICIDADE_CHOICES = [
        ('C', 'C'),
        ('B', 'B'),
        ('A', 'A'),
    ]
    codigo_sap = models.CharField(max_length=20, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    apelido_linha = models.TextField(max_length=200, blank=True, null=True)
    descricao_fornecedor = models.TextField(blank=True, null=True)
    quantidade = models.IntegerField(default=0)
    quantidade_minima = models.IntegerField(blank=True, null=True)
    quantidade_maxima = models.IntegerField(blank=True, null=True)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True)
    localizacao = models.CharField(max_length=100, default='')
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

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request:
            if not self.pk:  # Novo objeto
                self.criado_por = request.user
            else:  # Objeto existente
                self.alterado_por = request.user
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request:
            self.deletado_por = request.user
            self.save()  # Atualiza o campo deletado_por antes de deletar
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.item.nome_sap if self.item else 'Sem nome'

    def valor_total(self):
        if self.quantidade is not None and self.valor_unitario is not None:
            return self.quantidade * self.valor_unitario
        return None

    def status_quantidade(self):
        if self.quantidade is not None and self.quantidade_minima is not None and self.margem_proximo_minimo is not None:
            if self.quantidade <= self.quantidade_minima:
                return "vermelho"
            elif self.quantidade <= self.quantidade_minima + self.margem_proximo_minimo:
                return "amarelo"
            else:
                return "verde"
        return None
