import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Фильтр для /api/products/
    Примеры:
      /api/products/?category=govyadina
      /api/products/?is_new=true
      /api/products/?min_price=1000&max_price=3000
    """
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="exact")
    is_new = django_filters.BooleanFilter(field_name="is_new")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "is_new", "min_price", "max_price", "in_stock"]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)