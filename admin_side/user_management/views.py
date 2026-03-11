from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_staff


@never_cache
@login_required(login_url='admin-login')
@user_passes_test(is_admin)
def admin_user_management(request):

    search = request.GET.get("search")

    users = User.objects.filter(is_staff=False)

    if search:
        users = users.filter(email__icontains=search)

    users = users.order_by("-date_joined")

    paginator = Paginator(users, 5)

    page = request.GET.get("page")

    users = paginator.get_page(page)

    return render(request, "admin/admin_user_management.html", {"users": users})


@never_cache
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_toggle_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    user.is_active = not user.is_active
    user.save()

    return redirect('admin-user-management')


@never_cache
def admin_logout(request):
    logout(request)
    return redirect("admin-login")


