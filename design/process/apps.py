from django.apps import AppConfig

class ProcessConfig(AppConfig):
    name = 'process'
    verbose_name = 'Process Manager'
    def ready(self):
        pass # add startup code here
