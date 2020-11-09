from django.apps import AppConfig


class PathwaysConfig(AppConfig):
    name = 'pathways'

    def ready(self):
        # pylint:disable=import-outside-toplevel
        # pylint:disable=unused-import
        import pathways.signals # noqa: F401
        # pylint:enable=import-outside-toplevel
        # pylint:enable=unused-import