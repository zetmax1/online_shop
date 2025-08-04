import django_filters

from products.models import Product


class ProductFilter(django_filters.FilterSet):
    price = django_filters.NumberFilter()
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    name = django_filters.CharFilter(lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='product_categories__category__name', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='product_categories__category__id')

    class Meta:
        model = Product
        fields = ('price', 'name', 'category_name', 'category')
