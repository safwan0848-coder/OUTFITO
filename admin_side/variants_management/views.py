from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import IntegrityError
from admin_side.products_management.models import Product
import re
from decimal import Decimal, InvalidOperation
from django.db import transaction
from admin_side.variants_management.models import Variant
from admin_side.products_management.utils import generate_sku
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test

# ✅ 1. VARIANT LIST
def is_admin(user):
    return user.is_authenticated and user.is_staff

SIZES            = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
MAX_IMAGE_SIZE   = 5 * 1024 * 1024
ALLOWED_TYPES    = ['image/jpeg', 'image/png', 'image/webp']


@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def variant_list(request, product_id):

    # ----------------------------
    # Session (optional, safe)
    # ----------------------------
    request.session['last_admin_page'] = 'variant_list'

    # ----------------------------
    # Get product
    # ----------------------------
    product = get_object_or_404(
        Product,
        id=product_id,
        is_deleted=False
    )

    # ----------------------------
    # Get variants
    # ----------------------------
    variants = product.variants.filter(
        is_active=True
    ).order_by('-is_default', 'id')

    # ----------------------------
    # Render (NO CHANGE)
    # ----------------------------
    return render(request, 'admin/variant_list.html', {
        'product': product,
        'variants': variants
    })




@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def add_variant(request, product_id):

    # ----------------------------
    # Session (safe)
    # ----------------------------
    request.session['last_admin_page'] = 'add_variant'

    # ----------------------------
    # Get product
    # ----------------------------
    product = get_object_or_404(
        Product,
        id=product_id,
        is_deleted=False
    )

    # ----------------------------
    # GET request
    # ----------------------------
    if request.method != 'POST':
        return render(request, 'admin/add_variant.html', {
            'product': product,
            'sizes': SIZES,
            'old': None,
        })

    # ----------------------------
    # Read POST data
    # ----------------------------
    size = request.POST.get('size', '').strip().upper()
    if not size:
        size = request.POST.get('size_hidden', '').strip().upper()

    color     = request.POST.get('color', '').strip()
    price_raw = request.POST.get('price', '').strip()
    stock_raw = request.POST.get('stock', '').strip()
    is_active = request.POST.get('is_active') == 'on'
    is_default = request.POST.get('is_default') == 'on'

    image_cover = request.FILES.get('image')
    image_side  = request.FILES.get('image_side')
    image_back  = request.FILES.get('image_back')

    # ----------------------------
    # Fail helper (no break)
    # ----------------------------
    def fail(msg):
        messages.error(request, msg)
        return render(request, 'admin/add_variant.html', {
            'product': product,
            'sizes': SIZES,
            'old': request.POST,
        })

    # ----------------------------
    # Validation
    # ----------------------------
    if size not in SIZES:
        return fail('Please select a valid size.')

    if not color:
        return fail('Color is required.')

    if not re.match(r'^([A-Za-z\s]+|#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}))$', color):
        return fail('Color must be letters or valid hex (#FF0000).')

    try:
        price = Decimal(price_raw)
        if price <= 0:
            raise ValueError
    except:
        return fail('Price must be greater than 0.')

    try:
        stock = int(stock_raw)
        if stock < 0:
            raise ValueError
    except:
        return fail('Stock must be non-negative.')

    if not image_cover:
        return fail('Cover image is required.')

    # ----------------------------
    # Image validation
    # ----------------------------
    for img, label in [
        (image_cover, 'Cover'),
        (image_side,  'Side'),
        (image_back,  'Back')
    ]:
        if img:
            if img.size > MAX_IMAGE_SIZE:
                return fail(f'{label} image must be under 5MB.')
            if img.content_type not in ALLOWED_TYPES:
                return fail(f'{label} image must be JPG, PNG or WEBP.')

    # ----------------------------
    # Save variant
    # ----------------------------
    try:
        with transaction.atomic():

            # Prevent duplicate variant
            if Variant.objects.filter(
                product=product,
                size=size,
                color=color,
                is_active=True
            ).exists():
                return fail("This variant already exists.")

            # Temporary object for SKU
            temp = Variant(product=product, size=size, color=color)

            # Generate unique SKU
            for _ in range(10):
                sku = generate_sku(product, temp)
                if not Variant.objects.filter(sku=sku).exists():
                    break
            else:
                return fail("Unable to generate unique SKU")

            # Create variant
            variant = Variant.objects.create(
                product=product,
                sku=sku,
                size=size,
                color=color,
                price=price,
                stock=stock,
                image=image_cover,
                is_active=is_active,
                is_default=is_default,
            )

            # Ensure only one default
            if is_default:
                Variant.objects.filter(
                    product=product
                ).exclude(id=variant.id).update(is_default=False)

    except IntegrityError:
        return fail('SKU already exists. Try again.')
    except Exception as e:
        return fail(f'Error: {e}')

    # ----------------------------
    # Success
    # ----------------------------
    messages.success(request, f'Variant "{sku}" added successfully.')
    return redirect('variant_list', product_id=product.id)

 
 
@never_cache
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def edit_variant(request, variant_id):

    # ----------------------------
    # Session (safe)
    # ----------------------------
    request.session['last_admin_page'] = 'edit_variant'

    # ----------------------------
    # Get variant + product
    # ----------------------------
    variant = get_object_or_404(Variant, id=variant_id)
    product = variant.product

    # ----------------------------
    # GET request
    # ----------------------------
    if request.method != 'POST':
        return render(request, 'admin/edit_variant.html', {
            'variant': variant,
            'sizes':   SIZES,
        })

    # ----------------------------
    # Read POST data
    # ----------------------------
    size = request.POST.get('size', '').strip().upper()
    if not size:
        size = request.POST.get('size_hidden', '').strip().upper()

    color      = request.POST.get('color', '').strip()
    price_raw  = request.POST.get('price', '').strip()
    stock_raw  = request.POST.get('stock', '').strip()
    is_active  = request.POST.get('is_active')  == 'on'
    is_default = request.POST.get('is_default') == 'on'

    new_cover = request.FILES.get('image')
    new_side  = request.FILES.get('image_side')
    new_back  = request.FILES.get('image_back')

    keep_cover = request.POST.get('keep_image',      '0') == '1'
    keep_side  = request.POST.get('keep_image_side', '0') == '1'
    keep_back  = request.POST.get('keep_image_back', '0') == '1'

    # ----------------------------
    # Validation
    # ----------------------------
    errors = []

    if size not in SIZES:
        errors.append('Please select a valid size.')

    if not color:
        errors.append('Color is required.')
    elif not re.match(r'^([A-Za-z\s]+|#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}))$', color):
        errors.append('Color must be letters or valid hex (#FF0000).')

    try:
        price = Decimal(price_raw)
        if price <= 0:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        errors.append('Price must be greater than 0.')
        price = None

    try:
        stock = int(stock_raw)
        if stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        errors.append('Stock must be non-negative.')
        stock = None

    # ----------------------------
    # Image validation
    # ----------------------------
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

    cover_ok = (keep_cover and variant.image) or (new_cover is not None)
    if not cover_ok:
        errors.append('Cover image is required.')

    # ----------------------------
    # Show errors
    # ----------------------------
    if errors:
        for err in errors:
            messages.error(request, err)

        return render(request, 'admin/edit_variant.html', {
            'variant': variant,
            'sizes':   SIZES,
        })

    # ----------------------------
    # Save changes
    # ----------------------------
    try:
        with transaction.atomic():

            variant.size      = size
            variant.color     = color
            variant.price     = price
            variant.stock     = stock
            variant.is_active = is_active

            # Default handling
            if is_default:
                Variant.objects.filter(
                    product=product
                ).exclude(id=variant.id).update(is_default=False)
                variant.is_default = True
            else:
                variant.is_default = False

            # Cover image
            if new_cover:
                if variant.image:
                    variant.image.delete(save=False)
                variant.image = new_cover
            elif not keep_cover:
                if variant.image:
                    variant.image.delete(save=False)
                variant.image = None

            # Side image (Product)
            if new_side:
                if product.image_side:
                    product.image_side.delete(save=False)
                product.image_side = new_side
            elif not keep_side:
                if product.image_side:
                    product.image_side.delete(save=False)
                product.image_side = None

            # Back image (Product)
            if new_back:
                if product.image_back:
                    product.image_back.delete(save=False)
                product.image_back = new_back
            elif not keep_back:
                if product.image_back:
                    product.image_back.delete(save=False)
                product.image_back = None

            variant.save()
            product.save()

    except Exception as e:
        messages.error(request, f'Something went wrong: {e}')
        return render(request, 'admin/edit_variant.html', {
            'variant': variant,
            'sizes':   SIZES,
        })

    # ----------------------------
    # Success
    # ----------------------------
    messages.success(request, 'Variant updated successfully.')
    return redirect('variant_list', product_id=product.id)


# ✅ 4. DELETE VARIANT (soft delete better)
def delete_variant(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)

    variant.is_active = False
    variant.save()

    messages.success(request, "Variant removed")
    return redirect('variant_list', product_id=variant.product.id)


# ✅ 5. SET DEFAULT
def set_default_variant(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)

    Variant.objects.filter(product=variant.product).update(is_default=False)

    variant.is_default = True
    variant.save()

    messages.success(request, "Default variant updated")
    return redirect('variant_list', product_id=variant.product.id)