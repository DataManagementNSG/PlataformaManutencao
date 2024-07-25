from django.apps import AppConfig


class SolicitacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solicitacao'

    def ready(self):
        import solicitacao.signals  # noqa: F401