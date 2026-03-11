from django.urls import path
from . import views

urlpatterns = [
    path('admin-user-management/', views.admin_user_management, name='admin-user-management'),
    path("toggle-user/<int:user_id>/",views.admin_toggle_user,name="admin-toggle-user"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
]
