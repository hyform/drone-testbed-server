from django.apps import AppConfig


class AiConfig(AppConfig):
    name = 'ai'
    verbose_name = "AI Applications"
    def ready(self):
        pass # add startup code here
