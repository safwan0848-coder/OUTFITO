from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import  Prefetch
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product
from admin_side.variants_management.models import Variant
from admin_side.categories_management.models import Category
from django.db import transaction, IntegrityError
import  re
from decimal import Decimal, InvalidOperation
from .utils import generate_sku
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff

VALID_TYPES = ['shirt', 'pant', 'tees', 'shorts']
VALID_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']


@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def product_list(request):

    search=request.GET.get('search', '').strip()
    category_id=request.GET.get('category', '')
    status=request.GET.get('status', '')

    products=Product.objects.filter(is_deleted=False).select_related('category')

    if search:
        products=products.filter(name__icontains=search)
    if category_id:
        products = products.filter(category_id=category_id)
    if status=='active':
        products=products.filter(is_listed=True)
    elif status=='inactive':
        products=products.filter(is_listed=False)

    products=products.order_by('-created_at').distinct()

    products=products.prefetch_related(
        Prefetch('variants',queryset=Variant.objects.filter(is_default=True),to_attr='default_variant'))

    paginator=Paginator(products, 5)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    for product in page_obj:
        dv=getattr(product, 'default_variant', [])
        product.display_variant=dv[0] if dv else product.variants.first()

    categories=Category.objects.filter(is_deleted=False)

    context={
        'products':page_obj,
        'categories':categories,
        'search':search,
        'selected_category':category_id,
        'selected_status':status,
    }

    return render(request,'admin/product_list.html', context)


@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def add_product(request):

    categories = Category.objects.filter(is_deleted=False,is_active=True)

    if request.method != 'POST':
        return render(request, 'admin/add_product.html', {
            'categories': categories,
            'sizes': SIZES,'old': None,})

    name=request.POST.get('name', '').strip()
    description=request.POST.get('description', '').strip()
    category_id=request.POST.get('category', '').strip()
    product_type=request.POST.get('product_type', '').strip()
    size=request.POST.get('size', '').strip().upper()
    price_raw=request.POST.get('price', '').strip()
    stock_raw=request.POST.get('stock', '').strip()
    color=request.POST.get('color', '').strip()
    is_active=request.POST.get('is_active') == 'on'

    image_cover=request.FILES.get('image_cover')
    image_side=request.FILES.get('image_side')
    image_back=request.FILES.get('image_back')

    def fail(msg):
        messages.error(request, msg)
        return render(request, 'admin/add_product.html', {
            'categories': categories,
            'sizes': SIZES,
            'old': request.POST,
        })

    if not name or len(name) < 7:
        return fail('Product name must be at least 7 characters.')

    if not re.match(r'^[A-Za-z0-9\s\-\']+$', name):
        return fail('Invalid product name.')

    if len(description) > 1000:
        return fail('Description too long.')

    if not category_id:
        return fail('Select category.')

    if product_type not in VALID_TYPES:
        return fail('Invalid product type.')

    if size not in SIZES:
        return fail('Invalid size.')

    if not color or not re.match(r'^([A-Za-z\s]+|#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}))$', color):
        return fail('Invalid color.')
    
    if not price_raw:
        return fail('Price is required.')

    try:
        price=Decimal(price_raw)
        if price <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return fail('Invalid price.')

    try:
        stock=int(stock_raw)
        if stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        return fail('Invalid stock.')

    if not image_cover or not image_side or not image_back:
        return fail('Minimum 3 images required.')

    if image_cover.size > MAX_IMAGE_SIZE:
        return fail('Cover image too large.')

    if image_cover.content_type not in ALLOWED_TYPES:
        return fail('Invalid cover image.')
    
    for img, label in [(image_side, 'Side'), (image_back, 'Back')]:
        if img:
            if img.size > MAX_IMAGE_SIZE:
                return fail(f'{label} image too large.')
            if img.content_type not in ALLOWED_TYPES:
                return fail(f'Invalid {label} image.')

    try:
        category = Category.objects.get( id=category_id,is_deleted=False,is_active=True)
    except Category.DoesNotExist:
        return fail('Invalid category.')

    try:
        with transaction.atomic():

            product=Product.objects.create(
                name=name,
                description=description,
                category=category,
                product_type=product_type,
                is_listed=True,
                image_side=image_side if image_side else None,
                image_back=image_back if image_back else None,)
            variant=Variant(
                product=product,
                size=size,
                color=color,
                price=price,
                stock=stock,
                image=image_cover,
                is_active=is_active,
                is_default=True,
            )
            variant.sku = generate_sku(product, variant)
            variant.save()

    except IntegrityError:
        return fail('Duplicate error.')
    except Exception as e:
        return fail(f'Error: {e}')

    messages.success(request, f'Product "{name}" added successfully.')
    return redirect('product_list')
 
@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def edit_product(request, pk):

    product=get_object_or_404(Product,pk=pk,is_deleted=False)

    variant=(product.variants.filter(is_default=True).first() or product.variants.first())

    categories=Category.objects.filter(is_deleted=False,is_active=True).order_by('category_name')

    VALID_TYPES=['shirt', 'pant', 'tees', 'shorts']

    if request.method=='POST':

        errors=[]

        name=request.POST.get('name', '').strip()
        description=request.POST.get('description', '').strip()
        category_id=request.POST.get('category', '').strip()
        product_type=request.POST.get('product_type', '').strip()
        size=request.POST.get('size', '').strip().upper()
        price_raw=request.POST.get('price', '').strip()
        stock_raw=request.POST.get('stock', '').strip()
        color=request.POST.get('color', '').strip().title()
        is_active=request.POST.get('is_active') == 'on'

        new_cover = request.FILES.get('image_cover')
        new_side  = request.FILES.get('image_side')
        new_back  = request.FILES.get('image_back')

        keep_cover = request.POST.get('keep_image_cover', '0') == '1'
        keep_side  = request.POST.get('keep_image_side',  '0') == '1'
        keep_back  = request.POST.get('keep_image_back',  '0') == '1'

        if not name or len(name) < 7:
            errors.append('Product name must be at least 7 characters.')
        elif not re.match(r'^[A-Za-z0-9\s\-\']+$', name):
            errors.append('Product name contains invalid characters.')

        if description and len(description) > 1000:
            errors.append('Description must be under 1000 characters.')

        category = None
        if not category_id:
            errors.append('Please select a category.')
        else:
            try:
                category = Category.objects.get(pk=category_id,is_deleted=False,is_active=True)
            except Category.DoesNotExist:
                errors.append('Selected category does not exist.')

        if product_type not in VALID_TYPES:
            errors.append('Please select a valid product type.')

        if size not in SIZES:
            errors.append('Please select a valid size.')

        if not color:
            errors.append('Color is required.')
        elif not re.match(r'^([A-Za-z\s]+|#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}))$', color):
            errors.append('Color must contain only letters.')

        try:
            price = Decimal(price_raw)
            if price <= 0:
                raise ValueError
        except (InvalidOperation, ValueError, TypeError):
            errors.append('Price must be a number greater than 0.')
            price = None

        try:
            stock = int(stock_raw)
            if stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Stock must be a non-negative integer.')
            stock = None

        for img_file, label in [
            (new_cover, 'Cover'),
            (new_side,  'Side'),
            (new_back,  'Back')
        ]:
            if img_file:
                if img_file.size > MAX_IMAGE_SIZE:
                    errors.append(f'{label} image must be under 5 MB.')
                elif img_file.content_type not in ALLOWED_TYPES:
                    errors.append(f'{label} image: invalid type.')

        cover_ok = (keep_cover and variant and variant.image) or (new_cover is not None)
        if not cover_ok:
            errors.append('Cover image is required.')

        if errors:
            for err in errors:
                messages.error(request, err)

            return render(request, 'admin/edit_product.html', {
                'product':product,
                'variant':variant,
                'categories': categories,
                'sizes':SIZES,
                'old':request.POST,
            })

        try:
            with transaction.atomic():

                product.name= name
                product.description= description
                product.category= category
                product.product_type= product_type
                product.is_listed = is_active

                if not variant:
                    variant = Variant(
                        product=product,
                        sku=generate_sku(),
                        is_default=True,)

                variant.size= size
                variant.color= color
                variant.price= price
                variant.stock= stock
                variant.is_active= is_active
                variant.is_default= True

                Variant.objects.filter(product=product).exclude(id=variant.id).update(is_default=False)

                if new_cover:
                    if variant.image:
                        variant.image.delete(save=False)
                    variant.image = new_cover
                elif not keep_cover:
                    if variant.image:
                        variant.image.delete(save=False)
                    variant.image = None

                if new_side:
                    product.image_side = new_side
                elif not keep_side:
                    if product.image_side:
                        product.image_side.delete(save=False)
                    product.image_side = None

                if new_back:
                    product.image_back = new_back
                elif not keep_back:
                    if product.image_back:
                        product.image_back.delete(save=False)
                    product.image_back = None

                product.save()
                variant.save()

        except Exception:
            messages.error(request, 'Something went wrong while updating.')
            return render(request, 'admin/edit_product.html', {
                'product':    product,
                'variant':    variant,
                'categories': categories,
                'sizes':      SIZES,
                'old':        request.POST,
            })

        messages.success(request, f'Product "{product.name}" updated successfully.')
        return redirect('product_list')

    return render(request, 'admin/edit_product.html', {
        'product':    product,
        'variant':    variant,
        'categories': categories,
        'sizes':      SIZES,
        'old':        None,
    })

def delete_product(request, pk):
    product=get_object_or_404(Product, pk=pk)

    if request.method=='POST':
        name = product.name
        product.is_deleted=True
        product.save()
        messages.success(request, f'Product "{name}" has been deleted.')
        return redirect('product_list')

    return redirect('edit_product', pk=pk)

def toggle_product_status(request, pk):
    product = get_object_or_404(Product, pk=pk)

    product.is_listed = not product.is_listed
    product.save()

    return redirect('product_list')