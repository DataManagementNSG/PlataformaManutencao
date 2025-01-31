from django.shortcuts import get_object_or_404
from spare.models import Material
from outflows.models import Outflow
from accounts.models import Usuario
import json
import openai
from django.conf import settings
from django.core import serializers
from ai import prompts, models
from datetime import datetime
from django.utils.timezone import make_aware


class SGEAgent:
    def __init__(self, user=None):
        self.user = user
        openai.api_key = settings.OPENAI_API_KEY

    def __get_data(self):
        try:
            usuario = get_object_or_404(Usuario, user=self.user)
            materials = Material.objects.filter(setor=usuario.setor, quantidade__lt=5).order_by('item__nome_sap')[:5]

            # Converta a data para um objeto com timezone
            start_date = make_aware(datetime(2024, 1, 1))
            outflows = Outflow.objects.filter(criado_em__gte=start_date)[:5]

            return json.dumps({
                'materials': serializers.serialize('json', materials),
                'outflows': serializers.serialize('json', outflows),
            })
        except Exception as e:
            raise Exception(f"Erro ao buscar dados: {e}")

    def invoke(self):
        try:
            data = self.__get_data()
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': prompts.SYSTEM_PROMPT,
                    },
                    {
                        'role': 'user',
                        'content': prompts.USER_PROMPT.replace('{{data}}', data),
                    },
                ],
            )
            result = response['choices'][0]['message']['content']
            models.AIResult.objects.create(result=result)
        except Exception as e:
            print(f"Erro ao invocar OpenAI: {e}")
            # Log o erro em vez de apenas imprimir (opcional)
            # logger.error(f"Erro ao invocar OpenAI: {e}")

