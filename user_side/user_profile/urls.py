from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path("edit-profile/", views.edit_profile, name="edit-profile"),
    path('change-password/', views.change_password, name="change-password"),
    path('start-password-reset/', views.start_password_reset, name='start-password-reset'),
    path('profile-reset-verify/', views.profile_reset_verify, name='profile-reset-verify'),
    path('profile-set-new-password/', views.profile_set_new_password, name='profile-set-new-password'),
    path('address/', views.address, name='address'),
    path('wallet/', views.wallet, name='wallet'),
    path('orders/', views.orders, name='orders'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.wishlist, name='wishlist'),
    path("verify-email-change/", views.verify_email_change, name="verify-email-change"),
    path("resend-profile-otp/", views.resend_profile_otp, name="resend-profile-otp"),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)