from django.urls import path
from . import views

urlpatterns = [
    path('',views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('otp/', views.otp_verify, name='otp_verify'),
    path('resend-signup-otp/', views.resend_signup_otp, name='resend-signup-otp'),
    path("resend-reset-otp/",views.resend_reset_otp,name="resend-reset-otp"),
    path('change-email/',views.change_email, name='change_email'),
    path('forgot-password/',views.forgot_password, name='forgot_password'),
    path('reset-verify/',views.reset_verify, name='reset_verify'),
    path('set-new-password/',views.set_new_password, name='set_new_password'),
    path('back-login/',views.back_to_login, name='back_to_login'),
    path('address/', views.address, name='address'),
    path('wallet/', views.wallet, name='wallet'),
    path('orders/', views.orders, name='orders'),
    path('logout/', views.logout_view, name='logout'),
    
]