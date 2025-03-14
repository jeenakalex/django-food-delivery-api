from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView,DestroyAPIView,UpdateAPIView,CreateAPIView,RetrieveUpdateAPIView
from .serializers import UserSerializer, AgentSerializer, UpdateAgentSerializer, UpdateCustomerSerializer, CustomerSerializer, CustomerListSerializer
from .permissions import IsAdminUser, IsCustomer
from .models import UserProfile
from order.models import Order



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to  include custom data and return a token 
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    """_summary_

    Args:
        TokenObtainPairView (_type_): _description_
    """
    serializer_class = CustomTokenObtainPairSerializer


class CreateAgentView(CreateAPIView):
    """
    View for create agent
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AgentSerializer
    
    def post(self, request, *args, **kwargs):
        """Function to create agent"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Agent created successfully!.","data":AgentSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UpdateAgentView(UpdateAPIView):
    """
    View for updating agent details (Only ADMINs can update).
    """
    permission_classes = [IsAuthenticated, IsAdminUser] 
    serializer_class = UpdateAgentSerializer
    queryset = UserProfile.objects.filter(role="AGENT")
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        """Update function"""
        agent = self.get_object()
        serializer = self.get_serializer(agent, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Agent updated successfully!"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AgentListView(ListAPIView):
    """Class have some features which displays list of all registered agents"""
    serializer_class = AgentSerializer

    def get_queryset(self):
        """Return only users with role AGENT"""
        return UserProfile.objects.filter(role="AGENT", status="ACTIVE")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"message": "Agent list retrieved successfully!", "data": serializer.data},
            status=status.HTTP_200_OK
        )
        

class AvailableAgentListView(ListAPIView):
    """Class have some features which displays list of all registered agents"""
    serializer_class = AgentSerializer

    def get_queryset(self):
        """Return only users with role AGENT"""
        return UserProfile.objects.filter(role="AGENT", status="ACTIVE", agent_status="AVAILABLE")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"message": "Agent list retrieved successfully!", "data": serializer.data},
            status=status.HTTP_200_OK
        )
        

class UpdateCustomerView(UpdateAPIView):
    """
    View for updating Customer details.
    """
    permission_classes = [IsAuthenticated, IsAdminUser] 
    serializer_class = UpdateCustomerSerializer
    queryset = UserProfile.objects.filter(role="CUSTOMER")
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        """Update function"""
        agent = self.get_object()
        serializer = self.get_serializer(agent, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer updated successfully!"}, status=status.HTTP_200_OK)   
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CustomerSignupView(CreateAPIView):
    """
    View for create agent
    """
    serializer_class = CustomerSerializer
    
    def post(self, request, *args, **kwargs):
        """Function to create agent"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Customer created successfully!.","data":CustomerSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class DeleteUserProfileView(APIView):
    """API to allow customers to soft delete their profile"""

    permission_classes = [IsAuthenticated, IsCustomer]

    def delete(self, request):
        """Soft delete customer if no pending/assigned orders exist"""
        customer = request.user
        
        # Check if customer has pending or assigned orders
        has_orders = Order.objects.filter(customer=customer, status__in=['pending', 'assigned']).exists()
        
        if has_orders:
            return Response({"error": "Cannot delete profile. You have pending or assigned orders."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Perform soft delete
        customer.soft_delete()
        
        return Response({"message": "Profile deleted successfully."}, status=status.HTTP_200_OK)

class CustomerListView(ListAPIView):
    """API to list all customers with their order details"""
    queryset = UserProfile.objects.filter(role='CUSTOMER')
    serializer_class = CustomerListSerializer
    permission_classes = [IsAuthenticated]