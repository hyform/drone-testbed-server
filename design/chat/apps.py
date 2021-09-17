from django.apps import AppConfig

class ChatConfig(AppConfig):
    name = 'chat'
    verbose_name = 'Chat'
    def ready(self):
        pass # add startup code here