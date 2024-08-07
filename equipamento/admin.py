from django.contrib import admin
from .models import Linha, Area, Equipamento, HistoricoSubcomponente

admin.site.register(Linha)
admin.site.register(Area)
admin.site.register(Equipamento)
admin.site.register(HistoricoSubcomponente)