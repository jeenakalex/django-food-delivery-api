from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

# Customizing UserAdmin to use email as the unique identifier
class UserProfileAdmin(UserAdmin):
    model = UserProfile
    list_display = ('id','username','email', 'first_name', 'last_name', 'is_staff', 'is_active','role','status','created','agent_status')
   
    search_fields = ('email','role')
    ordering = ('email',)

# Registering User model with custom admin panel
admin.site.register(UserProfile, UserProfileAdmin)