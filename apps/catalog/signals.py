from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.catalog.models import Product


@receiver(post_save, sender=Product)
def product_post_save(sender: type, instance: Product, **kwargs: Any) -> None:
    """Imprime en consola cada vez que un Product es guardado."""
    print(
        f'[CATALOG] Producto "{instance.name}"'
        f" actualizado. Stock actual: {instance.stock}"
    )
