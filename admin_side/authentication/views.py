from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.contrib import messages


User = get_user_model()

@never_cache
def admin_login_view(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin-user-management')
    
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('landing')


    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect("admin-user-management")
        else:
            messages.error(request, "Invalid admin credentials")
            return redirect('admin-login')

    return render(request, "admin/admin_login.html")
