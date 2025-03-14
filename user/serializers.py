import random
import string
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, F
from rest_framework import serializers
from .models import UserProfile
from order.models import Order,OrderProduct
from user.utils import send_email


class UserSerializer(serializers.ModelSerializer):
    """ User serializer """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
       
    
class AgentSerializer(serializers.ModelSerializer):
    """ Serializer for Agent """
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'role', 'email', 'phone_number', 'password', 'created','first_name','last_name','status','agent_status']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}
    
    def create(self, validated_data):
        """Function to create agent"""
        validated_data['role'] = 'AGENT'

        # Generate a random password
        auto_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        validated_data['password'] = make_password(auto_password)
        user_profile = UserProfile.objects.create(**validated_data)
        
        # Send email with login credentials
        subject = "Agent Account Created"
        message = f"Hello {user_profile.first_name},\n\nYour agent account has been created.\n\nLogin Credentials:\nUsername: {user_profile.username}\nPassword: {auto_password}\n\n."
        send_email(subject, message,user_profile.email)

        return user_profile
  
    
class UpdateAgentSerializer(serializers.ModelSerializer):
    """
    Serializer for updating agent details.
    Allows updating phone_number, first_name, last_name and status.   UpdateCustomerSerializer
    """
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'status','first_name','last_name']
        extra_kwargs = {
            'phone_number': {'required': False},
            'status': {'required': False}
        }   


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer signup"""
    
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    password = serializers.CharField()
    username =  serializers.CharField()
    
    
    class Meta:
        model = UserProfile
        fields = ['id','first_name', 'last_name', 'email', 'phone_number', 'password','username']

    def validate_email(self, value):
        """Ensure email is unique"""
        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Ensure username is unique"""
        if UserProfile.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        """Create a new customer"""
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['role'] = 'CUSTOMER'
        return UserProfile.objects.create(**validated_data)
    

class CustomerListSerializer(serializers.ModelSerializer):
    """Serializer for listing customers with order statistics"""

    total_orders = serializers.SerializerMethodField()
    total_amount_received = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number','status', 'total_orders', 'total_amount_received']

    def get_total_orders(self, obj):
        """Get total number of delivered orders by the customer"""
        return Order.objects.filter(customer=obj, status="delivered").count()

    def get_total_amount_received(self, obj):
        """Get total amount received from the customer using OrderProduct table"""
        total = OrderProduct.objects.filter(order__customer=obj, order__status="delivered") \
            .aggregate(total_amount=Sum(F('quantity') * F('price')))['total_amount']
        return total or 0.00

    
class UpdateCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customer details.
    Allows admin to block/unblock customer  
    """
    class Meta:
        model = UserProfile
        fields = ['status']
        extra_kwargs = {
            'status': {'required': False}
        } 
        
        