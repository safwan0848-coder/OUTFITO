from django.urls import path, include

urlpatterns = [
    path('', include('admin_side.authentication.urls')),
    path('', include('admin_side.user_management.urls')),
    path('', include('admin_side.products_management.urls')),
    path('', include('admin_side.categories_management.urls')),
    path('', include('admin_side.variants_management.urls')),
]