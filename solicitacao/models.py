from django.db import models
from django.contrib.auth.models import User
from equipamento.models import Equipamento, Linha, Criticidade, Area
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from accounts.models import Setor

class Turno(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class OpcaoChecklist(models.Model):
    letra = models.CharField(max_length=1, primary_key=True)
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.letra} - {self.descricao}"

class Solicitacao(models.Model):
    id = models.AutoField(primary_key=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    autor = models.CharField(max_length=100)
    linha = models.ForeignKey(Linha, on_delete=models.CASCADE, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    criticidade = models.ForeignKey(Criticidade, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    componente = models.CharField(max_length=100)
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    opcoes_checklist = models.ManyToManyField(OpcaoChecklist)
    descricao = models.TextField(blank=True, null=True)
    data_fechamento = models.DateTimeField(blank=True, null=True)
    tipo_problema = models.CharField(max_length=20, choices=(('Mecânico', 'Mecânico'), ('Eletrônico', 'Eletrônico')), default='Mecânico')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return str(self.id)
    
    def esta_concluida(self):
        return self.data_fechamento is not None
    
    def calcular_data_limite(self):
        hoje = timezone.now()
        if self.criticidade.nome == 'A':
            prazo = 2  # Prazo em dias
        elif self.criticidade.nome == 'B':
            prazo = 11  # Prazo em dias
        else:
            ultimo_dia_mes = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            prazo = (ultimo_dia_mes.date() - self.data_criacao.date()).days
    
        return self.data_criacao + timedelta(days=prazo)


    def esta_atrasada(self):
        if self.esta_concluida():
            return False
        return self.calcular_data_limite() < timezone.now()


logger = logging.getLogger(__name__)
@receiver(post_save, sender=Solicitacao)
def enviar_email_solicitacao_atrasada(sender, instance, created, **kwargs):
    if not created and instance.esta_atrasada() and not instance.esta_concluida():
        logger.info(f"Enviando e-mail para solicitação atrasada: {instance}")
        print("Enviando e-mail para solicitação atrasada:", instance)
        subject = 'Solicitação PM em Atraso!'
        html_message = render_to_string('solicitacao_atrasada.html', {'solicitacao': instance})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        
        # Obtém os responsáveis pelo equipamento associado à solicitação
        responsaveis = []

        if instance.tipo_problema == 'Mecânico':
            if instance.equipamento.responsavel_mecanico and instance.equipamento.responsavel_mecanico.email:
                responsaveis.append(instance.equipamento.responsavel_mecanico.email)
        elif instance.tipo_problema == 'Eletrônico':
            if instance.equipamento.responsavel_eletronico and instance.equipamento.responsavel_eletronico.email:
                responsaveis.append(instance.equipamento.responsavel_eletronico.email)

        logger.info(f"Responsáveis: {responsaveis}")

        if responsaveis:
            # Envia o e-mail
            sent = send_mail(subject, plain_message, from_email, responsaveis, html_message=html_message)
            if sent > 0:
                logger.info("E-mail enviado com sucesso!")
                print("E-mail enviado com sucesso!")
            else:
                logger.error("Falha ao enviar o e-mail.")
                print("Falha ao enviar o e-mail.")



