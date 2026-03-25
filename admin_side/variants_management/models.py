from django.db import models
from admin_side.products_management.models import Product


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=100, unique=True)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sku
    

    def save(self, *args, **kwargs):
        if self.color:
            self.color = self.color.strip().lower()
        super().save(*args, **kwargs)
    

    
