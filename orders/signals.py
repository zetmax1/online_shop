from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Order, OrderItem


@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    order = instance.order
    total = sum(
        item.product.price * item.quantity
        for item in order.items.select_related('product')
    )
    order.total_amount = total
    order.save()
