from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    PRODUCT_STATUS = (
        ('AVAILABLE', 'AVAILABLE'),
        ('UNAVAILABLE', 'UNAVAILABLE')
    )
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.CharField(_('Status'), choices=PRODUCT_STATUS, max_length=50, default='AVAILABLE', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
