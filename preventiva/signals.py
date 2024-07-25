from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from preventiva.models import Preventiva

class Atividade(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Atividade")
    preventiva = models.ForeignKey(Preventiva, on_delete=models.CASCADE, related_name='atividades')

@receiver(post_save, sender=Preventiva)
def buscar_atividades(sender, instance, created, **kwargs):
    if created:  # Verifica se a preventiva foi recém-criada
        # Busca as atividades relacionadas ao texto breve da preventiva
        atividades_relacionadas = Atividade.objects.filter(nome__icontains=instance.texto_breve)
        # Adiciona as atividades encontradas à preventiva
        instance.atividades.set(atividades_relacionadas)
