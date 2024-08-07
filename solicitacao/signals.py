import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Solicitacao

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

        if instance.equipamento.responsavel_mecanico and instance.equipamento.responsavel_mecanico.especialidade == 'Mecânico':
            if instance.equipamento.responsavel_mecanico.email:
                responsaveis.append(instance.equipamento.responsavel_mecanico.email)
        
        if instance.equipamento.responsavel_eletronico and instance.equipamento.responsavel_eletronico.especialidade == 'Eletrônico':
            if instance.equipamento.responsavel_eletronico.email:
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
