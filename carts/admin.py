from django.contrib import admin

from carts.models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('total_price',)
    list_display = ('user', 'total_price', 'is_ordered')

admin.site.register(Cart)
admin.site.register(CartItem)