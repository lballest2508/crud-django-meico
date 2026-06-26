from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Configuración de la app Catalog."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"

    def ready(self) -> None:
        """Registra los signals al iniciar Django."""
        import apps.catalog.signals  # noqa: F401
