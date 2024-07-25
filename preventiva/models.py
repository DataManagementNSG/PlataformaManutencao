from django.db import models
from tecnicos.models import Tecnicos
from django.utils import timezone
from accounts.models import Setor

class Preventiva(models.Model):
    tipo_ordem = models.CharField(max_length=100)
    loc_instalacao = models.CharField(max_length=100)
    denominacao = models.CharField(max_length=100)
    nota = models.TextField(default='Default note value')  # Valor padrão para nota
    ordem = models.CharField(max_length=100, unique=True)
    texto_breve = models.CharField(max_length=200)
    liberacao_real = models.DateTimeField(null=True, blank=True)
    data_base_inic = models.DateField(null=True, blank=True)
    data_base_fim = models.DateField(null=True, blank=True)
    inic_real_hr = models.DateTimeField(null=True, blank=True)
    fim_real_hr = models.DateTimeField(null=True, blank=True)
    criado_por = models.CharField(max_length=100)
    centro_custo = models.CharField(max_length=100)
    total_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status_sistema = models.CharField(max_length=100)
    status_preventiva = models.BooleanField(default=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    tempo_execucao = models.CharField(max_length=100, null=True, blank=True)
    comentarios = models.TextField(null=True, blank=True)
    lancado_no_sap = models.BooleanField(default=False)
    centro_trabalho_responsavel = models.CharField(max_length=100, blank=True, null=True)
    responsavel = models.ForeignKey(Tecnicos, on_delete=models.CASCADE, blank=True, null=True, related_name='preventivas')
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def status(self):
        if not self.status_preventiva:
            return 'Fechada'
        if self.data_base_fim and self.data_base_fim < timezone.now().date():
            return 'Em Atraso'
        return 'Aberta'

    def __str__(self):
        return self.texto_breve

class Tarefa(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self):
        return self.nome


class Atividade(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Atividade")
    preventivas = models.ManyToManyField(Preventiva, related_name='atividades', blank=True)
    tarefas = models.ManyToManyField(Tarefa, related_name='atividades', blank=True)


    def __str__(self):
        return self.nome