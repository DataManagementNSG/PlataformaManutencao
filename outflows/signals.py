from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from outflows.models import Outflow
from spare.models import Material
from django.contrib.auth.models import User  # Importe do modelo User
import logging
from django.conf import settings  # Importe das configurações de e-mail
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def enviar_email_quantidade_minima_atingida(spare, responsavel_email):
    # Renderiza o template do e-mail
    subject = 'Alerta de quantidade mínima atingida para: {}'.format(spare.item)
    message = render_to_string('email.html', {'spare': spare})
    plain_message = strip_tags(message)
    # Envie o e-mail para o responsável
    send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [responsavel_email], html_message=message)


@receiver(post_save, sender=Outflow)
def update_spare_quantidade(sender, instance, **kwargs):
    if instance.quantidade > 0:
        try:
            spare = Material.objects.get(codigo_sap=instance.codigo_sap)
            if instance.quantidade > spare.quantidade:
                raise ValidationError(f"Tentativa de registrar uma saída com quantidade maior do que o estoque disponível para o material {spare.item}.")
            else:
                spare.quantidade -= instance.quantidade
                spare.save()
                # Verifica se a quantidade atual está abaixo do mínimo e envia um e-mail se necessário
                if spare.quantidade <= spare.quantidade_minima:
                    responsavel_email = spare.responsavel.email  # Acesse o e-mail do responsável
                    enviar_email_quantidade_minima_atingida(spare, responsavel_email)
        except ObjectDoesNotExist:
            # Se não houver Spare correspondente, emitimos um aviso.
            logger.warning(f"Spare com código SAP {instance.codigo_sap} não encontrado.")
