"""
URL configuration for outfito project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
app_name = "products_management"

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your custom auth app
    path('', include('user_side.authentication.urls')),
    path('user_profile/', include('user_side.user_profile.urls')),
    path('wishlist/', include('user_side.wishlist.urls')),
    path('address/', include('user_side.address.urls')),
    path('categories/', include('user_side.categories.urls')),
    path('products/', include('user_side.products.urls')),
    path('cart/', include('user_side.cart.urls')),


    path('admin_side/', include('admin_side.urls')),
    # THIS IS REQUIRED FOR GOOGLE LOGIN
    path('accounts/', include('allauth.urls')),
   
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)