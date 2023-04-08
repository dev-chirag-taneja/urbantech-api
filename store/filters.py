from django_filters.rest_framework import FilterSet

from store.models import Product

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'slug': ['exact'],
            'price': ['gt', 'lt'],
            'category_id': ['exact'],
            'color__name': ['icontains'],
            'size__name': ['icontains'],
        }