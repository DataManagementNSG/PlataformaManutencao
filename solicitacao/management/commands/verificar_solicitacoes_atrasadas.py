from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings  # Importe settings aqui
from solicitacao.models import Solicitacao
from datetime import timedelta  # Importe timedelta da biblioteca datetime
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Verifica solicitações em atraso e envia e-mails para os responsáveis'

    def calcular_data_limite(self, solicitacao):
        if solicitacao.criticidade.nome == 'A':
            prazo = 2  # Prazo em dias
        elif solicitacao.criticidade.nome == 'B':
            prazo = 7  # Prazo em dias
        else:
            hoje = timezone.now()
            ultimo_dia_mes = hoje.replace(day=1, month=hoje.month+1) - timedelta(days=1)
            prazo = (ultimo_dia_mes - solicitacao.data_criacao).days

        prazo = max(prazo, 0)
        return solicitacao.data_criacao + timedelta(days=prazo)

    def esta_atrasada(self, solicitacao):
        if solicitacao.data_fechamento:
            return False

        return self.calcular_data_limite(solicitacao) < timezone.now()

    def handle(self, *args, **kwargs):
        while True:
            logger.info("Verificando solicitações em atraso...")

            solicitacoes_atrasadas = Solicitacao.objects.filter(
            data_fechamento__isnull=True,
            data_criacao__lt=timezone.now()
            )

            for solicitacao in solicitacoes_atrasadas:
                if self.esta_atrasada(solicitacao):
                    logger.info(f"Enviando e-mail para solicitação atrasada: {solicitacao}")

                    subject = 'Solicitação PM em Atraso!'
                    html_message = render_to_string('solicitacao_atrasada.html', {'solicitacao': solicitacao})
                    plain_message = strip_tags(html_message)
                    from_email = settings.EMAIL_HOST_USER

                    responsaveis = []

                    if solicitacao.tipo_problema == 'Mecânico' and solicitacao.equipamento.responsavel_mecanico:
                        responsaveis.append(solicitacao.equipamento.responsavel_mecanico.email)
                    elif solicitacao.tipo_problema == 'Eletrônico' and solicitacao.equipamento.responsavel_eletronico:
                        responsaveis.append(solicitacao.equipamento.responsavel_eletronico.email)

                    logger.info(f"Responsáveis: {responsaveis}")

                    if responsaveis:
                        msg = EmailMultiAlternatives(subject, plain_message, from_email, responsaveis)
                        msg.attach_alternative(html_message, "text/html")

                        try:
                            msg.send()
                            logger.info("E-mail enviado com sucesso!")
                        except Exception as e:
                            logger.error(f"Falha ao enviar o e-mail: {str(e)}")

            logger.info("Verificação de solicitações em atraso concluída.")

            time.sleep(86400)