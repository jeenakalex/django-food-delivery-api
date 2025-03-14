from django.urls import path
from order.views import OrderCreateView, OrderListByCustomerView, OrderDetailView, UpdateOrderView, CancelOrderView, AssignAgentView, VerifyOrderOTPView


urlpatterns = [

    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('user/<int:customer_id>', OrderListByCustomerView.as_view(), name='order-list-by-customer'),
    path('<int:order_id>', OrderDetailView.as_view(), name='order-by-id'),
    path('<int:order_id>/update/', UpdateOrderView.as_view(), name='update-order'),
    path('<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    path('<int:order_id>/agentassign/', AssignAgentView.as_view(), name='agent-assign'),
    path('verify/', VerifyOrderOTPView.as_view(), name='verify-otp'),





  
]