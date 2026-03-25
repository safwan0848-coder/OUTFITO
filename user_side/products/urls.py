from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='user_product_list'),
    path('products/<int:pk>/',                views.product_detail,      name='product_detail'),

]