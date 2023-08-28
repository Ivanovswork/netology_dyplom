from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "app"

    def ready(self):
        """
        импортируем сигналы
        """
