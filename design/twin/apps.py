from django.apps import AppConfig

class TwinConfig(AppConfig):
    name = 'twin'
    verbose_name = 'Digital Twin'
    def ready(self):
        pass # add startup code here
