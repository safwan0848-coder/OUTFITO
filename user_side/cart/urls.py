# cart/urls.py

from django.urls import path
from . import views

 
urlpatterns = [
    path('cart/',                      views.cart_view,       name='cart_view'),
    path('cart/add/<int:pk>/',         views.add_to_cart,     name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_item,     name='remove_item'),
    path('cart/update/<int:item_id>/', views.update_cart_qty, name='update_cart_qty'),
]