from django.contrib import admin
from .models import Order, OrderProduct

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Register order model in Admin"""
    list_display = ('id','customer', 'agent', 'total_amount','status','created_at', 'updated_at', 'otp_code','payment_mode','cancel_reason')
    search_fields = ('customer', 'agent', 'status', 'created_at')
    list_filter = ('created_at', 'updated_at')
    
@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    """Register order product model in Admin"""
    list_display = ('id','order', 'product', 'quantity','price')
    search_fields = ('order', 'product')
