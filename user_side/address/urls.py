from django.urls import path
from . import views

urlpatterns = [
    path("address-list/", views.address_list, name="address-list"),
    path("add-address/", views.add_address, name="add-address"),
    path("edit-address/<int:id>/", views.edit_address, name="edit-address"),
    path("delete-address/<int:id>/", views.delete_address, name="delete-address"),
    path("set-default-address/<int:id>/", views.set_default_address, name="set-default-address"),
]