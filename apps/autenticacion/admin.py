from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models_notification import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'leida', 'archivada', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'archivada', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario__username', 'usuario__email')
    readonly_fields = ('fecha_creacion', 'fecha_lectura')
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'titulo', 'mensaje', 'tipo', 'icono')
        }),
        ('Acción', {
            'fields': ('url_accion', 'texto_accion')
        }),
        ('Estado', {
            'fields': ('leida', 'archivada')
        }),
        ('Metadata', {
            'fields': ('metadata', 'fecha_creacion', 'fecha_lectura'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha_creacion'
    
    actions = ['marcar_como_leidas', 'marcar_como_no_leidas', 'archivar_notificaciones']
    
    def marcar_como_leidas(self, request, queryset):
        updated = queryset.update(leida=True)
        self.message_user(request, f'{updated} notificaciones marcadas como leídas')
    marcar_como_leidas.short_description = 'Marcar seleccionadas como leídas'
    
    def marcar_como_no_leidas(self, request, queryset):
        updated = queryset.update(leida=False, fecha_lectura=None)
        self.message_user(request, f'{updated} notificaciones marcadas como no leídas')
    marcar_como_no_leidas.short_description = 'Marcar seleccionadas como no leídas'
    
    def archivar_notificaciones(self, request, queryset):
        updated = queryset.update(archivada=True)
        self.message_user(request, f'{updated} notificaciones archivadas')
    archivar_notificaciones.short_description = 'Archivar seleccionadas'

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