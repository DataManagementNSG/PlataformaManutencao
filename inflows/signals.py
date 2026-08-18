from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from inflows.models import Inflow
from spare.models import Material
from accounts.models import Usuario

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Inflow)
def update_spare_quantidade(sender, instance, **kwargs):
    if instance.quantidade <= 0:
        return

    try:
        # Verificar se o Inflow possui usuário
        if not instance.user:
            logger.warning(
                f"Inflow do código SAP {instance.codigo_sap} "
                f"não possui usuário associado."
            )
            return

        # Buscar o usuário do sistema
        usuario = Usuario.objects.get(user=instance.user)

        # Pegar o setor do usuário
        setor = usuario.setor

        # Buscar o Material pelo código SAP + setor
        spare = Material.objects.get(
            codigo_sap=instance.codigo_sap,
            setor=setor
        )

        # Atualizar quantidade
        spare.quantidade += instance.quantidade
        spare.save()

        logger.info(
            f"Estoque atualizado: SAP {instance.codigo_sap} | "
            f"Setor {setor} | "
            f"Quantidade adicionada: {instance.quantidade}"
        )

    except Usuario.DoesNotExist:
        logger.warning(
            f"Usuário {instance.user} não possui cadastro em Usuario."
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
            f"para o Inflow {instance.id}."
        )