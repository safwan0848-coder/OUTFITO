from django.urls import path
from . import views

urlpatterns = [

    path('add-category/', views.add_category, name='add_category'),
    path('category-list/', views.category_list, name='category_list'),

    path('toggle-category/<int:id>/', views.toggle_category_status, name='toggle_category_status'),
    path('edit-category/<int:id>/', views.edit_category, name='edit_category'),

    path('delete-category/<int:category_id>/',         views.delete_category,         name='delete_category'),

]