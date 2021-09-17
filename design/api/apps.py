from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'API'
    def ready(self):
        pass # add startup code here
