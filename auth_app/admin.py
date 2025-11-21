from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auth_app.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin-Interface für Custom User"""
    list_display = ['email', 'fullname', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['email', 'fullname']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('fullname',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('email', 'fullname', 'password1', 'password2')
        }),
    )