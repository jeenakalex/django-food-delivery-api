from django.urls import path
from user.views import CreateAgentView, UpdateAgentView, AgentListView, CustomerSignupView, AvailableAgentListView, DeleteUserProfileView, CustomerListView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView


urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('add-agent/',CreateAgentView.as_view(), name='create-agent'),
    path('update-agent/<int:id>/', UpdateAgentView.as_view(), name='update-agent'),
    path('list-agents/', AgentListView.as_view(), name='list-agents'),
    path('available-agents/', AvailableAgentListView.as_view(), name='available-agents-list'),
    path('signup/',CustomerSignupView.as_view(), name='customer-signup'),
    path('delete/',DeleteUserProfileView.as_view(), name='delete-user'),
    path('list-customers/', CustomerListView.as_view(), name='list-customers'),

]

