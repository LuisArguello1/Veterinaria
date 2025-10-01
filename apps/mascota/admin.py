from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from apps.mascota.models import Mascota, ImagenMascota, ModeloGlobal, EmbeddingStore, RegistroReconocimiento

# Registro de modelos para el panel administrativo

class ImagenMascotaInline(admin.TabularInline):
    model = ImagenMascota
    extra = 0
    readonly_fields = ('preview_imagen',)
    fields = ('imagen', 'preview_imagen', 'tipo', 'uploaded_at')
    
    def preview_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" height="75" />', obj.imagen.url)
        return "No hay imagen"
    
    preview_imagen.short_description = 'Vista previa'


class EmbeddingStoreInline(admin.TabularInline):
    model = EmbeddingStore
    extra = 0
    readonly_fields = ('creado',)


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'raza', 'sexo', 'edad_completa', 'preview_foto_perfil', 'imagenes_count', 'biometria_entrenada')
    list_filter = ('biometria_entrenada', 'sexo', 'etapa_vida', 'estado_corporal')
    search_fields = ('nombre', 'propietario__first_name', 'propietario__last_name', 'propietario__username', 'raza')
    readonly_fields = ('created_at', 'updated_at', 'imagenes_count', 'preview_foto_perfil')
    inlines = [ImagenMascotaInline, EmbeddingStoreInline]
    
    fieldsets = (
        ('Información básica', {
            'fields': (('nombre', 'propietario'), 'raza', 'color', 'sexo', 'foto_perfil', 'preview_foto_perfil')
        }),
        ('Características físicas', {
            'fields': (('edad', 'edad_unidad'), 'fecha_nacimiento', 'peso', 'etapa_vida', 'estado_corporal')
        }),
        ('Datos adicionales', {
            'classes': ('collapse',),
            'fields': ('caracteristicas_especiales', 'metadata')
        }),
        ('Información biométrica', {
            'fields': ('biometria_entrenada', 'confianza_biometrica')
        }),
        ('Metadatos', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'imagenes_count')
        }),
    )
    
    def preview_foto_perfil(self, obj):
        if obj.foto_perfil:
            return format_html('<img src="{}" height="50" />', obj.foto_perfil.url)
        return "Sin foto de perfil"
    
    preview_foto_perfil.short_description = 'Foto de perfil'
    
    def imagenes_count(self, obj):
        count = obj.imagenes.count()
        url = reverse('admin:mascota_imagenmascota_changelist') + f'?mascota__id__exact={obj.id}'
        return format_html('<a href="{}">{} imágenes</a>', url, count)
    
    imagenes_count.short_description = 'Imágenes'


@admin.register(ImagenMascota)
class ImagenMascotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mascota_nombre', 'preview_imagen', 'tipo', 'uploaded_at')
    list_filter = ('tipo', 'uploaded_at')
    search_fields = ('mascota__nombre',)
    raw_id_fields = ('mascota',)
    
    def mascota_nombre(self, obj):
        return obj.mascota.nombre
    
    def preview_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" height="50" />', obj.imagen.url)
        return "No hay imagen"
    
    mascota_nombre.short_description = 'Mascota'
    preview_imagen.short_description = 'Imagen'


@admin.register(EmbeddingStore)
class EmbeddingStoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'mascota_nombre', 'dimension', 'modelo_extractor', 'usado_en_entrenamiento', 'creado')
    list_filter = ('modelo_extractor', 'usado_en_entrenamiento', 'creado')
    search_fields = ('mascota__nombre',)
    
    def mascota_nombre(self, obj):
        return obj.mascota.nombre
    
    mascota_nombre.short_description = 'Mascota'


@admin.register(ModeloGlobal)
class ModeloGlobalAdmin(admin.ModelAdmin):
    list_display = ('id', 'activo', 'version', 'created_at', 'metricas_precision')
    list_filter = ('activo', 'version', 'created_at')
    readonly_fields = ('created_at', 'mascotas_entrenadas')
    
    def mascotas_entrenadas(self, obj):
        if obj.metadatos and 'mascotas_incluidas' in obj.metadatos:
            count = len(obj.metadatos['mascotas_incluidas'])
            return f"{count} mascotas"
        return "0 mascotas"
    
    def metricas_precision(self, obj):
        if obj.metricas and 'precision' in obj.metricas:
            return f"{obj.metricas['precision'] * 100:.1f}%"
        return "-"
    
    mascotas_entrenadas.short_description = 'Mascotas entrenadas'
    metricas_precision.short_description = 'Precisión'


@admin.register(RegistroReconocimiento)
class RegistroReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'exito', 'mascota_predicha_nombre', 'confianza_percent', 'fecha', 'preview_imagen')
    list_filter = ('exito', 'fecha')
    readonly_fields = ('fecha', 'preview_imagen')
    
    def mascota_predicha_nombre(self, obj):
        if obj.mascota_predicha:
            return obj.mascota_predicha.nombre
        return "-"
    
    def confianza_percent(self, obj):
        if obj.confianza is not None:
            return f"{obj.confianza * 100:.1f}%"
        return "-"
    
    def preview_imagen(self, obj):
        if obj.imagen_analizada:
            return format_html('<img src="{}" height="50" />', obj.imagen_analizada.url)
        return "No hay imagen"
    
    mascota_predicha_nombre.short_description = 'Mascota'
    confianza_percent.short_description = 'Confianza'
    preview_imagen.short_description = 'Imagen'
