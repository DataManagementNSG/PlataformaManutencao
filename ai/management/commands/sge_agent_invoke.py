from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ai.agent import SGEAgent


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Seleciona um usuário fixo ou o primeiro da base de dados
        user = User.objects.first()  # Substitua pelo critério desejado
        
        if not user:
            self.stdout.write(self.style.ERROR('Nenhum usuário encontrado.'))
            return

        agent = SGEAgent(user=user)
        agent.invoke()

        self.stdout.write(self.style.SUCCESS('SGE AGENT INVOCADO COM SUCESSO!'))
