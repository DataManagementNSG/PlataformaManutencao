# signals.py
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import Material
from spare.middleware import get_current_request

@receiver(pre_save, sender=Material)
def set_criado_alterado_por(sender, instance, **kwargs):
    request = get_current_request()
    if instance.pk is None:
        # Novo objeto
        if request:
            instance.criado_por = request.user
    else:
        # Objeto existente
        if request:
            instance.alterado_por = request.user

@receiver(pre_delete, sender=Material)
def set_deletado_por(sender, instance, **kwargs):
    request = get_current_request()
    if request:
        instance.deletado_por = request.user
        instance.save()
