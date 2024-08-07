import threading
from django.core.management import call_command
from django.conf import settings
import time

class StartScriptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.script_thread = None

    def __call__(self, request):
        if not self.script_thread or not self.script_thread.is_alive():
            self.script_thread = threading.Thread(target=self.start_script)
            self.script_thread.daemon = True
            self.script_thread.start()

        response = self.get_response(request)
        return response

    def start_script(self):
        # Inicia o comando desejado (verificar_solicitacoes_atrasadas é um comando personalizado)
        try:
            call_command('verificar_solicitacoes_atrasadas')
        except Exception as e:
            # Trate exceções, se necessário
            print(f"Erro ao executar o comando: {str(e)}")
