from django.contrib import admin
from .models import Prioridade, Status, Ordem, MaterialOrdem, Falhas

admin.site.register(Prioridade)
admin.site.register(Status)
admin.site.register(Ordem)
admin.site.register(MaterialOrdem)
admin.site.register(Falhas)