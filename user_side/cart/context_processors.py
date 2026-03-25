from .models import Cart as _Cart   # relative import inside the same app
 
 
def cart_count(request):

    if not request.user.is_authenticated:
        return {'cart_count': 0}
 
    try:
        cart  = _Cart.objects.prefetch_related('items').get(user=request.user)
        count = sum(i.quantity for i in cart.items.all())
    except _Cart.DoesNotExist:
        count = 0
 
    return {'cart_count': count}