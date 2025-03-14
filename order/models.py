from django.db import models
from user.models import UserProfile
from product.models import Product

class Order(models.Model):
    """Order Model """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    PAYMENT_MODES = [
        ('cod', 'COD')
    ]

    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders')
    agent = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', limit_choices_to={'role': 'agent'})
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='cod')
    cancel_reason =  models.CharField(max_length=100,blank=True, null=True)


    def __str__(self):
        return str(self.id)
    
     
class OrderProduct(models.Model):
    """Order - product model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def get_total_price(self):
        """Calculate total price for the product in the order"""
        return float(self.quantity * self.price) 
