from django.urls import path
from . import views

urlpatterns = [
    path('product_list/', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('products/<int:pk>/edit/',    views.edit_product,   name='edit_product'),
    path('products/<int:pk>/delete/',  views.delete_product, name='delete_product'),
    path('products/<int:pk>/toggle/', views.toggle_product_status, name='toggle_product_status'),
]