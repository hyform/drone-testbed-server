from django.apps import AppConfig


class RepoConfig(AppConfig):
    name = 'repo'
    verbose_name = 'Repo'
    def ready(self):
        pass # add startup code here