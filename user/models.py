from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserProfile(AbstractUser):
    """  Add extra fields to user by Extending Django's default User model """
    USER_ROLES = (
        ('ADMIN', 'ADMIN'),
        ('AGENT', 'AGENT'),
        ('CUSTOMER', 'CUSTOMER'),
    )
    USER_STATUS = (
        ('ACTIVE', 'ACTIVE'),
        ('BLOCKED', 'BLOCKED'),
        ('DELETED', 'DELETED'),
    )
    
    AGENT_STATUS = (
        ('AVAILABLE', 'AVAILABLE'),
        ('UNAVAILABLE', 'UNAVAILABLE')
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(_('Status'), choices=USER_STATUS, max_length=50, default='ACTIVE', blank=True)
    role = models.CharField(_('User Role'), choices=USER_ROLES, max_length=50, null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name="user_profiles", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_profiles_permissions", blank=True)
    created  = models.DateTimeField(_('Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Modified'), auto_now_add=True)
    agent_status =  models.CharField(_('Agent Status'), choices=AGENT_STATUS, max_length=50, default='AVAILABLE', blank=True)
    
    def __str__(self):
        return str(self.username)

    def soft_delete(self):
        """Mark user as deleted instead of actually deleting"""
        self.status = 'DELETED'
        self.save(update_fields=['status'])