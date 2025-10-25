from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserFaceEmbedding

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


@admin.register(UserFaceEmbedding)
class UserFaceEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('user', 'confidence_score', 'is_active', 'allow_login', 'successful_logins', 'created_at')
    list_filter = ('is_active', 'allow_login', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'successful_logins', 'failed_attempts', 'last_successful_login')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Datos Biométricos', {
            'fields': ('descriptor_data', 'confidence_score', 'face_bbox')
        }),
        ('Estado y Permisos', {
            'fields': ('is_active', 'allow_login')
        }),
        ('Estadísticas', {
            'fields': ('successful_logins', 'failed_attempts', 'last_successful_login')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Deshabilitar creación manual desde admin
        return False

admin.site.register(User, CustomUserAdmin)