# utils.py

from .models import Preventiva, Atividade

def vincular_atividades(preventiva):
    atividades = Atividade.objects.filter(preventiva__texto_breve=preventiva.texto_breve)
    for atividade in atividades:
        atividade.preventiva = preventiva
        atividade.save()
