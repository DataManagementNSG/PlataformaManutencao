from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from inflows.models import Inflow  # Importe do modelo Inflow
from spare.models import Material  # Importe do modelo Spare

import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Inflow)
def update_spare_quantidade(sender, instance, **kwargs):
    if instance.quantidade > 0:
        try:
            spare = Material.objects.get(codigo_sap=instance.codigo_sap)
            spare.quantidade += instance.quantidade
            spare.save()
        except ObjectDoesNotExist:
            # Se não houver Spare correspondente, emitimos um aviso.
            logger.warning(f"Spare com código SAP {instance.codigo_sap} não encontrado.")
