import random
from user.utils import send_email

from rest_framework import serializers
from .models import Order, OrderProduct
from product.models import Product
from django.conf import settings


class OrderProductSerializer(serializers.ModelSerializer):
    """Serializer for OrderProduct model """
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['product_id', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model with multiple products"""
    items = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'agent', 'total_amount', 'status', 'payment_mode', 'created_at', 'updated_at', 'items']

    def create(self, validated_data):
        """Create an order"""
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderProduct.objects.create(order=order, **item_data)
        
        # Generate and send OTP
        otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
        order.otp_code = otp
        order.save()
        # Send OTP via email
        subject = "Your Order OTP"
        message = f"Dear {order.customer.first_name},\n\nYour OTP for order verification is {otp}. Please use this OTP to verify the order upon delivery."
        send_email(subject, message, order.customer.email)

        return order

    def update(self, instance, validated_data):
        """Update order and its items"""
        items_data = validated_data.pop('items', [])
        instance.total_amount = validated_data.get('total_amount', instance.total_amount)
        instance.status = validated_data.get('status', instance.status)
        instance.payment_mode = validated_data.get('payment_mode', instance.payment_mode)
        instance.save()

        # Update Order Items
        instance.items.all().delete()  # Remove old order items
        for item_data in items_data:
            OrderProduct.objects.create(order=instance, **item_data)

        return instance
