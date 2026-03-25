 
from django.db import models
from django.conf import settings
from admin_side.products_management.models import Product
from admin_side.variants_management.models import Variant
 
 
class Cart(models.Model):
    user       = models.OneToOneField(       # OneToOne: one cart per user
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"Cart({self.user.username})"
 
    @property
    def total_items(self):
        return sum(i.quantity for i in self.items.all())
 
    @property
    def subtotal(self):
        return sum(i.variant.price * i.quantity for i in self.items.all())
 
 
class CartItem(models.Model):
    cart     = models.ForeignKey(Cart,    on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant  = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
 
    class Meta:
        unique_together = ('cart', 'variant')   # prevent duplicate rows
 
    def __str__(self):
        return f"{self.product.name} × {self.quantity}"
 
    @property
    def subtotal(self):
        return self.variant.price * self.quantity