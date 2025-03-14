from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission for admin.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user.is_authenticated and request.user.is_staff
    
class IsCustomer(permissions.BasePermission):
    """
    Custom permission for customer.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user.is_authenticated and request.user.role == 'CUSTOMER' and request.user.status == 'ACTIVE'
    
class IsAgent(permissions.BasePermission):
    """
    Custom permission for customer.
    """

    def has_permission(self, request, view):
        """Check if agent is authenticated"""
        return request.user.is_authenticated and request.user.role == 'AGENT' and request.user.status == 'ACTIVE'
    