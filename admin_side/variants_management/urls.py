from django.urls import path
from . import views

urlpatterns = [
    path('variants/<int:product_id>/', views.variant_list, name='variant_list'),
    path('variants/add/<int:product_id>/', views.add_variant, name='add_variant'),
    path('variants/edit/<int:variant_id>/', views.edit_variant, name='edit_variant'),
    path('variants/delete/<int:variant_id>/', views.delete_variant, name='delete_variant'),
    path('variants/default/<int:variant_id>/', views.set_default_variant, name='set_default_variant'),
]