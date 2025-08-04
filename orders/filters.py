import django_filters

from orders.models import Order


class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='iexact')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['status', 'created_at']
