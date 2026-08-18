from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from outflows.models import Outflow
from spare.models import Material
from accounts.models import Usuario
import logging
from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def enviar_email_quantidade_minima_atingida(spare, responsavel_email):
    subject = 'Alerta de quantidade mínima atingida para: {}'.format(
        spare.item
    )

    message = render_to_string(
        'email.html',
        {'spare': spare}
    )

    plain_message = strip_tags(message)

    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [responsavel_email],
        html_message=message
    )


@receiver(post_save, sender=Outflow)
def update_spare_quantidade(sender, instance, **kwargs):

    if instance.quantidade <= 0:
        return

    try:
        # Verifica se existe usuário associado à saída
        if not instance.user:
            logger.warning(
                f"Outflow do código SAP {instance.codigo_sap} "
                f"não possui usuário associado."
            )
            return

        # Buscar o usuário no modelo Usuario
        usuario = Usuario.objects.get(
            user=instance.user
        )

        # Pegar o setor do usuário
        setor = usuario.setor

        # Buscar o Material pelo código SAP + setor
        spare = Material.objects.get(
            codigo_sap=instance.codigo_sap,
            setor=setor
        )

        # Verificar se existe estoque suficiente
        if instance.quantidade > spare.quantidade:
            raise ValidationError(
                f"Tentativa de registrar uma saída com quantidade "
                f"maior do que o estoque disponível para o material "
                f"{spare.item}."
            )

        # Retirar a quantidade do estoque
        spare.quantidade -= instance.quantidade
        spare.save()

        logger.info(
            f"Estoque atualizado: "
            f"SAP {instance.codigo_sap} | "
            f"Setor {setor} | "
            f"Quantidade retirada: {instance.quantidade} | "
            f"Estoque restante: {spare.quantidade}"
        )

        # Verifica se atingiu a quantidade mínima
        if (
            spare.quantidade_minima is not None
            and spare.quantidade <= spare.quantidade_minima
        ):
            if spare.responsavel and spare.responsavel.email:
                responsavel_email = spare.responsavel.email

                enviar_email_quantidade_minima_atingida(
                    spare,
                    responsavel_email
                )

    except Usuario.DoesNotExist:
        logger.warning(
            f"Usuário {instance.user} "
            f"não possui cadastro em Usuario."
        )

    except Material.DoesNotExist:
        logger.warning(
            f"Material com código SAP {instance.codigo_sap} "
            f"não encontrado no setor {setor}."
        )

    except Material.MultipleObjectsReturned:
        logger.error(
            f"Existem múltiplos materiais com o código SAP "
            f"{instance.codigo_sap} no setor {setor}."
        )

    except ObjectDoesNotExist:
        logger.warning(
            f"Não foi possível localizar os dados necessários "
            f"para o Outflow {instance.id}."
        )