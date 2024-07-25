from django.contrib import admin
from .models import Tarefa, Atividade, Preventiva

admin.site.register(Tarefa)
admin.site.register(Preventiva)
admin.site.register(Atividade)