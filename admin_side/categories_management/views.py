import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Category
from admin_side.products_management.models import Product
from django.db.models import Count,Q
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff


@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def add_category(request):

    if request.method=="POST":

        name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, "Category name is required.")
            return redirect('add_category')

        if not re.match(r'^[A-Za-z ]+$', name):
            messages.error(request, "Only letters allowed.")
            return redirect('add_category')

        if Category.objects.filter(category_name__iexact=name,is_deleted=False).exists():
            messages.error(request, "Category already exists.")
            return redirect('add_category')

        Category.objects.create(category_name=name,description=description,image=image,is_active=is_active)

        messages.success(request, "Category added successfully.")
        return redirect('category_list')

    return render(request, "admin/add_category.html")



@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def category_list(request):

    search_query=request.GET.get('search', '').strip()

    categories=Category.objects.filter(is_deleted=False).annotate(product_count=Count('products'))

    if search_query:
        categories=categories.filter(category_name__icontains=search_query)

    categories=categories.order_by('-created_at')

    paginator=Paginator(categories, 5)
    page_number=request.GET.get('page')
    categories=paginator.get_page(page_number)

    total_categories=Category.objects.filter(is_deleted=False).count()
    active_categories=Category.objects.filter(is_active=True,is_deleted=False).count()
    inactive_categories=Category.objects.filter(is_active=False,is_deleted=False).count()

    context={
        "categories":categories,
        "search_query":search_query,
        "total_categories":total_categories,
        "active_categories":active_categories,
        "inactive_categories":inactive_categories
    }

    return render(request,"admin/category_list.html", context)



def toggle_category_status(request, id):

    category=get_object_or_404(Category, id=id, is_deleted=False)

    category.is_active=not category.is_active
    category.save()
    return redirect('category_list')


@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def edit_category(request, id):

    category=get_object_or_404(Category,id=id,is_deleted=False)

    if request.method=="POST":

        name=request.POST.get("category_name", '').strip()
        description=request.POST.get("description", '').strip()
        image=request.FILES.get("image")
        is_active=request.POST.get("is_active")=="on"

        if not name:
            messages.error(request, "Category name required")
            return redirect('edit_category', id=id)

        if not re.match(r'^[A-Za-z ]+$', name):
            messages.error(request, "Only letters allowed")
            return redirect('edit_category', id=id)

        if Category.objects.filter(category_name__iexact=name,is_deleted=False).exclude(id=id).exists():
            messages.error(request, "Category already exists")
            return redirect('edit_category', id=id)

        category.category_name=name
        category.description=description
        category.is_active=is_active

        if image:
            category.image=image

        category.save()

        messages.success(request, "Category updated successfully")
        return redirect("category_list")

    return render(request, "admin/edit_category.html", {"category": category})


def delete_category(request, category_id):
    if request.method=='POST':
        category=get_object_or_404(Category, id=category_id)
        name=category.category_name

        category.is_deleted=True
        category.save(update_fields=['is_deleted'])

        messages.success(request, f'Category "{name}" deleted successfully.')
    return redirect('category_list')