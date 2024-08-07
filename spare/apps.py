from django.apps import AppConfig

class SpareConfig(AppConfig):
    name = 'spare'

    def ready(self):
        import spare.signals
