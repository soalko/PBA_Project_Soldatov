from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.db.models import CharField
from django.db.models.functions import Lower


def unicode_lower(value):
    """Перевести строку в нижний регистр средствами Python."""
    if isinstance(value, str):
        return value.lower()
    return value


def register_unicode_lower(sender, connection, **kwargs):
    """Заменить функцию LOWER в SQLite на Unicode-версию.

    Встроенные LOWER и LIKE в SQLite меняют регистр только у
    латиницы: LOWER('ОКТЯБРЬ') остаётся 'ОКТЯБРЬ', поэтому
    icontains не находит «Октябрьский» по запросу «октябрь».
    SQLite разрешает переопределить встроенную функцию своей,
    это и делается для каждого нового соединения с базой.
    """
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            "LOWER", 1, unicode_lower, deterministic=True,
        )


class HomepageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "homepage"

    def ready(self):
        # Сигнал отправляется при открытии каждого соединения.
        connection_created.connect(register_unicode_lower)
        # Разрешает писать в запросах name__lower__contains=...:
        # сначала LOWER(name), затем поиск подстроки.
        CharField.register_lookup(Lower)
