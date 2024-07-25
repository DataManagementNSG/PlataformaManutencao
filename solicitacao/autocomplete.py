from dal import autocomplete
from .models import Equipamento

class EquipamentoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        queryset = Equipamento.objects.all()

        linha_id = self.forwarded.get('linha', None)
        area_id = self.forwarded.get('area', None)

        if linha_id:
            queryset = queryset.filter(linha_id=linha_id)
        if area_id:
            queryset = queryset.filter(area_id=area_id)

        queryset = queryset.order_by('nome')

        return queryset
