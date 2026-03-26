from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Min, Max, Q
 
from admin_side.products_management.models import Product
from admin_side.categories_management.models import Category
from admin_side.variants_management.models import Variant

SORT_OPTIONS = [
    ('default',    'Featured'),
    ('price_asc',  'Price: Low to High'),
    ('price_desc', 'Price: High to Low'),
    ('newest',     'Newest First'),
    ('name_asc',   'Name: A–Z'),
]
 
SIZE_ORDER = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
 
def user_category_list(request):
    """
    Shows the categories grid — each card links to
    product_list?category=<id> which auto-applies the filter.
    """
    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(product_count=Count(
            'products',
            filter=Q(products__is_listed=True, products__is_deleted=False)
        ))
        .order_by('category_name')
    )
 
    return render(request, 'user/categories.html', {
        'categories': categories,
    })
 