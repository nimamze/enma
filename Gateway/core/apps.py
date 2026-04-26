from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        import Project.Enma.Gateway.core.utils.signals
