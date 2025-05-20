from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'is_host', 'is_staff', 'is_active')
    list_filter = ('is_host', 'is_staff', 'is_active')
    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_host', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'full_name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)

