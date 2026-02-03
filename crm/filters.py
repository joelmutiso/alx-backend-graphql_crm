import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    # Case-insensitive partial matches
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date range filters
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'created_at']

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    # Price ranges
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Stock ranges
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

class OrderFilter(django_filters.FilterSet):
    # Date ranges
    order_date__gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date__lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')

    # Amount ranges
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')

    # Related field filtering (Magic happens here!)
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date', 'customer', 'products']