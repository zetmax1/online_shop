from django.db import models

from shared.models import BaseModel


class Cart(BaseModel):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='cart')
    is_ordered = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.email}'s cart"

    @property
    def get_total_price(self):
        total = sum(item.product.price * item.quantity for item in self.items.all())
        return round(total, 2)

    def update_total_price(self):
        self.total_price = self.get_total_price
        self.save(update_fields=["total_price"])
    class Meta:
        db_table = 'carts'
        verbose_name = 'cart'
        verbose_name_plural = 'carts'
        ordering = ['-created_at']


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cart.user.email} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cart.update_total_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.cart.update_total_price()
