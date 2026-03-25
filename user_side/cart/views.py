from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

from .models import Cart, CartItem
from admin_side.variants_management.models import Variant

# ── Maximum quantity allowed per line item ──
MAX_QTY = 5


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_or_create_cart(user):
    """Return user's cart safely."""

    if not user.is_authenticated:
        return None   # important: avoid crash

    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def _variant_is_purchasable(variant):
    """
    Returns (ok: bool, reason: str).
    Checks variant active status, product listed/not-deleted, and stock > 0.
    """
    product = variant.product

    if not variant.is_active:
        return False, "This variant is no longer available."

    if product.is_deleted or not product.is_listed:
        return False, f"'{product.name}' is currently unavailable."

    if variant.stock <= 0:
        return False, f"'{product.name}' ({variant.size} / {variant.color}) is out of stock."

    return True, ""


# ─────────────────────────────────────────────
# ADD TO CART  (POST from product_detail)
# ─────────────────────────────────────────────

@login_required
@require_POST
def add_to_cart(request, pk):

    # ✅ USE pk FROM URL (IMPORTANT FIX)
    variant = get_object_or_404(Variant, pk=pk)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    quantity = max(1, quantity)
    action = request.POST.get('action', 'cart')

    # ✅ SAFETY CHECK (VERY IMPORTANT)
    if not variant.is_active or variant.stock <= 0:
        messages.error(request, "This product is not available.")
        return redirect(request.META.get('HTTP_REFERER', 'user_product_list'))

    cart = get_or_create_cart(request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            'product': variant.product,
            'quantity': 0,
        }
    )

    new_qty = item.quantity + quantity

    # ✅ STOCK VALIDATION
    if new_qty > variant.stock:
        if item.quantity >= variant.stock:
            messages.warning(
                request,
                f"Maximum available stock ({variant.stock}) already in cart."
            )
            return redirect(request.META.get('HTTP_REFERER', 'user_product_list'))

        new_qty = variant.stock
        messages.warning(request, f"Only {variant.stock} available. Quantity adjusted.")

    # ✅ MAX LIMIT
    MAX_QTY = 5
    if new_qty > MAX_QTY:
        new_qty = MAX_QTY
        messages.warning(request, f"Maximum {MAX_QTY} units allowed.")

    item.quantity = new_qty
    item.save()

    # ✅ REMOVE FROM WISHLIST
    try:
        from .models import Wishlist
        Wishlist.objects.filter(
            user=request.user,
            product=variant.product
        ).delete()
    except Exception:
        pass

    messages.success(request, f"'{variant.product.name}' added to cart!")

    if action == 'buy':
        return redirect('cart_view')

    return redirect(request.META.get('HTTP_REFERER', 'user_product_list'))

@never_cache
@login_required(login_url='login')
def cart_view(request):

    # ----------------------------
    # Session (optional, safe)
    # ----------------------------
    request.session['last_page'] = 'cart_view'

    # ----------------------------
    # Get cart + items
    # ----------------------------
    cart = get_or_create_cart(request.user)

    items = list(
        cart.items
        .select_related('product', 'variant')
        .order_by('id')
    )

    # ----------------------------
    # Initialize totals
    # ----------------------------
    subtotal   = 0
    discount   = 0
    has_oos    = False
    item_count = 0

    # ----------------------------
    # Calculate totals
    # ----------------------------
    for item in items:

        v = item.variant

        # Check unavailable / out of stock
        if (
            not v.is_active or
            v.product.is_deleted or
            not v.product.is_listed or
            v.stock == 0
        ):
            has_oos = True

        subtotal   += item.subtotal
        item_count += item.quantity

        # Discount calculation
        if (
            hasattr(v, 'original_price') and
            v.original_price and
            v.original_price > v.price
        ):
            discount += (v.original_price - v.price) * item.quantity

    # ----------------------------
    # Shipping + total
    # ----------------------------
    shipping = 0 if subtotal >= 499 else 49
    total    = subtotal - discount + shipping

    # ----------------------------
    # Render (NO CHANGE)
    # ----------------------------
    return render(request, 'user/cart.html', {
        'items':      items,
        'item_count': item_count,
        'subtotal':   subtotal,
        'discount':   discount,
        'shipping':   shipping,
        'total':      total,
        'savings':    discount,
        'has_oos':    has_oos,
        'max_qty':    MAX_QTY,
    })

@never_cache
@login_required(login_url='login')
@require_POST
def update_cart_qty(request, item_id):

    # ----------------------------
    # Session (optional, safe)
    # ----------------------------
    request.session['last_action'] = 'update_cart_qty'

    # ----------------------------
    # Get cart item
    # ----------------------------
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    action = request.POST.get('action', 'increment')
    v      = item.variant

    # ----------------------------
    # Re-check variant availability
    # ----------------------------
    ok, reason = _variant_is_purchasable(v)

    if not ok:
        messages.error(request, reason)
        return redirect('cart_view')

    # ----------------------------
    # Increment quantity
    # ----------------------------
    if action == 'increment':

        if item.quantity >= v.stock:
            messages.warning(request, f"Only {v.stock} units in stock.")

        elif item.quantity >= MAX_QTY:
            messages.warning(request, f"Maximum {MAX_QTY} units per item.")

        else:
            item.quantity += 1
            item.save()

    # ----------------------------
    # Decrement quantity
    # ----------------------------
    elif action == 'decrement':

        if item.quantity <= 1:
            item.delete()
            messages.success(request, "Item removed from cart.")
            return redirect('cart_view')

        item.quantity -= 1
        item.save()

    # ----------------------------
    # Redirect (no change)
    # ----------------------------
    return redirect('cart_view')
# ─────────────────────────────────────────────
# REMOVE ITEM
# ─────────────────────────────────────────────

@login_required
@require_POST
def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    name = item.product.name
    item.delete()
    messages.success(request, f"'{name}' removed from cart.")
    return redirect('cart_view')

