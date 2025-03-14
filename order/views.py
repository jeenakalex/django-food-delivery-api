from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from user.permissions import IsAdminUser, IsCustomer, IsAgent
from django_filters.rest_framework import DjangoFilterBackend

from order.models import Order, OrderProduct
from product.models import Product
from user.models import UserProfile
from .serializers import OrderSerializer
from user.utils import send_email


class OrderCreateView(generics.ListCreateAPIView):
    """Create and list all Orders"""
    
    permission_classes = [IsAuthenticated, IsCustomer]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """create Order"""
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Order created successfully!", "data": response.data}, status=status.HTTP_201_CREATED)
    
class OrderListByCustomerView(generics.ListAPIView):
    """List all orders for the customer"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    
   
    def get_queryset(self):
        """Return orders that belong to the authenticated customer"""
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(UserProfile, id=customer_id) 
        return Order.objects.filter(customer=customer).order_by('-created_at')


    def list(self, request, *args, **kwargs):
        """Customize the response with a success message"""
        response = super().list(request, *args, **kwargs)
        return Response({"data": response.data}, status=status.HTTP_200_OK)
    
    
class OrderDetailView(generics.RetrieveAPIView):
    """API to retrieve a specific order by order ID"""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Fetch the order by ID"""
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(Order, id=order_id)

    def retrieve(self, request, *args, **kwargs):
        """Customize response with success message"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"message": "Order retrieved successfully", "data": serializer.data})
    


class CancelOrderView(APIView):
    """API for customers to cancel an order within 30 minutes"""

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """Cancel an order if conditions are met"""
        order = get_object_or_404(Order, id=order_id)
        is_customer = request.user.role == 'CUSTOMER' and order.customer == request.user
        is_admin = True
        order = get_object_or_404(Order, id=order_id)
     
        if is_customer:
            order = get_object_or_404(Order, id=order_id, customer=request.user)
            is_admin = False
            if order.status in ['assigned','delivered', 'cancelled']:
                return Response({"error": "Order cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)

            time_difference = now() - order.created_at
            if time_difference > timedelta(minutes=30):
                return Response({"error": "Order can only be cancelled within 30 minutes of creation"},
                                status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.cancel_reason = request.data.get("reason", "No reason provided")
        order.save()
        if is_admin:
            self.send_cancel_email(order, request.user)
            self.update_agent_status(order)
             
        return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)
    
    def update_agent_status(self, order):
        """Update agent status when an order is cancelled"""
        agent = order.agent 
        if agent:
            agent.agent_status = 'AVAILABLE'
            agent.save()
    
    def send_cancel_email(self, order, user):
        """Send cancel email to customer and agent"""
        subject = f"Order #{order.id} Cancellation Notification"
        customer_email = order.customer.email
        agent = order.agent
        message = f"Hello {order.customer.first_name},\n\nYour order #{order.id} has been cancelled.\n\nReason: {order.cancel_reason} \n\nIf you have any questions, please contact our support team.\n\n."
        send_email(subject, message,customer_email)
        if agent:
            message = f"Hello {agent.first_name},\n\n Order #{order.id} assigned to you has been cancelled.\n\nReason: {order.cancel_reason} \n\n."
            send_email(subject, message,agent.email)
          
  
    
class UpdateOrderView(APIView):
    """API for customers to update an order if it's in pending status"""

    permission_classes = [IsAuthenticated, IsCustomer]

    def put(self, request, order_id):
        """Update order details if it is still in pending status"""
        order = get_object_or_404(Order, id=order_id, customer= request.data.get("customer"))
        
        # Allow updates only if order is pending
        if order.status != 'pending':
            return Response({"error": "Order cannot be updated as it is not in pending status"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = request.data.get("total_amount", order.total_amount)
        payment_mode = request.data.get("payment_mode", order.payment_mode) or order.payment_mode
        items_data = request.data.get("items", [])
       
        if not items_data:
            return Response({"error": "At least one item is required to update the order."}, status=status.HTTP_400_BAD_REQUEST)
    
        order.items.all().delete()
        new_items = []
        for item in items_data:
           
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            price = item.get("price")
         
            if product_id and quantity and price:
                product = get_object_or_404(Product, id=product_id)
                new_items.append(OrderProduct(order=order, product=product, quantity=quantity, price=price))
                
        OrderProduct.objects.bulk_create(new_items)
        order.total_amount = total_amount
        order.payment_mode = payment_mode
        order.save()
        return Response({"message": "Order updated successfully", "data": OrderSerializer(order).data}, status=status.HTTP_200_OK)


class AssignAgentView(APIView):
    """API for assigning an agent to an order"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_id):
        """Assign an agent to an order"""
        order = get_object_or_404(Order, id=order_id)

        if order.agent is not None:
            return Response({"error": "Agent is already assigned to this order."}, status=status.HTTP_400_BAD_REQUEST)

        agent_id = request.data.get("agent_id")
        agent = get_object_or_404(UserProfile, id=agent_id, role="AGENT", status="ACTIVE", agent_status="AVAILABLE")
        order.agent = agent
        order.save()
        agent.agent_status = "UNAVAILABLE"
        agent.save()
        subject = "New Order Assigned"
        message = f"Dear {agent.first_name},\n\nWe are pleased to inform you that a new order has been assigned to you. Please find the details below:\n\nOrder Details:\nOrder ID:: {order.id}\nCustomer Name: {order.customer.first_name}\n\n."
        send_email(subject, message,agent.email)
        
        return Response({"message": "Agent assigned successfully", "agent": agent.first_name}, status=status.HTTP_200_OK)
    
class VerifyOrderOTPView(APIView):
    """API for agent to verify OTP for an order"""
    
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request):
        """Verify agent's OTP"""
        order_id = request.data.get("order_id")
        otp = request.data.get("otp")

        order = get_object_or_404(Order, id=order_id)

        if order.agent != request.user:
            return Response({"error": "You are not assigned to this order"}, status=status.HTTP_403_FORBIDDEN)

        if order.otp_code and order.otp_code == otp:
            order.status = "delivered"
            order.save()
            agent = order.agent
            agent.agent_status = 'AVAILABLE'
            agent.save()
            return Response({"message": "Order verified successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
