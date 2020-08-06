from django.apps import AppConfig


class PathwaysConfig(AppConfig):
    name = 'pathways'

    def ready(self):
        import pathways.signals