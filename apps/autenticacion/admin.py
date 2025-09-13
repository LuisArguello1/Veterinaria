from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'dni', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'dni', 'image', 'direction', 'phone')}),
        ('Rol y permisos', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Campos específicos por rol', {'fields': ('specialization', 'license_number')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información personal', {'fields': ('first_name', 'last_name', 'dni', 'image', 'direction', 'phone')}),
        ('Rol', {'fields': ('role',)}),
        ('Campos específicos por rol', {'fields': ('specialization', 'license_number')}),
    )
    
    search_fields = ('username', 'email', 'first_name', 'last_name', 'dni')

admin.site.register(User, CustomUserAdmin)