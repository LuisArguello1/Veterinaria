from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserFaceEmbedding, Notification

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


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'category', 'is_read', 'created_at')
    list_filter = ('notification_type', 'category', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'read_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Destinatario', {
            'fields': ('user',)
        }),
        ('Contenido', {
            'fields': ('notification_type', 'category', 'title', 'message', 'action_url')
        }),
        ('Relación', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected']
    
    def mark_as_read(self, request, queryset):
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1
        self.message_user(request, f'{count} notificaciones marcadas como leídas.')
    mark_as_read.short_description = "Marcar como leídas"
    
    def mark_as_unread(self, request, queryset):
        count = 0
        for notification in queryset:
            if notification.is_read:
                notification.mark_as_unread()
                count += 1
        self.message_user(request, f'{count} notificaciones marcadas como no leídas.')
    mark_as_unread.short_description = "Marcar como no leídas"
