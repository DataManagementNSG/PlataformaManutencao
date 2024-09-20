from django.contrib import admin
from .models import Categoria, Criticidade, Material, Unidade, Item

class CategoriaAdmin(admin.ModelAdmin):
    list_filter = ('nome',)  # Supondo que 'nome' seja um campo no modelo Categoria

class MaterialAdmin(admin.ModelAdmin):
    list_filter = ('setor', 'codigo_sap')  # Supondo que 'tipo' e 'categoria' sejam campos no modelo Material

class UnidadeAdmin(admin.ModelAdmin):
    list_filter = ('nome',)  # Supondo que 'nome' seja um campo no modelo Unidade

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Criticidade)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Unidade, UnidadeAdmin)
admin.site.register(Item)
