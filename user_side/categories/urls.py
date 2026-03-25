from django.urls import path
from . import views


urlpatterns = [
    path('collections/',  views.user_category_list, name='categories_page'),

]
