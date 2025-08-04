from django.contrib import admin

from orders.models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user__first_name', 'user__last_name', 'status')
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name')
    ordering = ('-created_at',)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order__user__first_name', 'product', 'quantity')
    list_filter = ('order',)
    search_fields = ('order',)
    ordering = ('order',)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)