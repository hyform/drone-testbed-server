from django.apps import AppConfig

class BotConfig(AppConfig):
    name = 'bot'
    verbose_name = 'Bot'
    def ready(self):
        pass # add startup code here
