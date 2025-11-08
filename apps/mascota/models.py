# apps/mascota/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import os
import uuid
from apps.autenticacion.models import User

def upload_to_mascota(instance, filename):
    """Guarda imágenes en MEDIA_ROOT/mascotas/<mascota_id>/<uuid>_<filename>"""
    ext = filename.split('.')[-1]
    name = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("mascotas", str(instance.mascota.id if instance.mascota_id else "temp"), name)

def upload_to_modelos(instance, filename):
    """Guarda modelos en MEDIA_ROOT/modelos/"""
    ext = filename.split('.')[-1]
    name = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"
    return os.path.join("modelos", name)


class Mascota(models.Model):
    # UUID para acceso público seguro (para QR codes)
    uuid = models.UUIDField(unique=True, editable=False, null=True, blank=True)
    
    ESTADO_CORPORAL_CHOICES = [
        ('delgado', 'Delgado'),
        ('normal', 'Normal'),
        ('obeso', 'Obeso')
    ]
    
    ETAPAS_VIDA_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('joven', 'Joven'),
        ('adulto', 'Adulto'),
        ('senior', 'Senior')
    ]
    
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('hembra', 'Hembra')
    ]
    
    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mascotas"
    )
    nombre = models.CharField(max_length=120)
    raza = models.CharField(max_length=120, blank=True, null=True)
    estado_corporal = models.CharField(
        max_length=20, 
        choices=ESTADO_CORPORAL_CHOICES, 
        blank=True, 
        null=True
    )
    etapa_vida = models.CharField(
        max_length=20, 
        choices=ETAPAS_VIDA_CHOICES, 
        blank=True, 
        null=True
    )
    edad = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    edad_unidad = models.CharField(
        max_length=5,
        choices=[('años', 'años'), ('meses', 'meses')],
        default='años'
    )
    sexo = models.CharField(
        max_length=12, 
        choices=SEXO_CHOICES, 
        blank=True, 
        null=True
    )
    fecha_nacimiento = models.DateField(blank=True, null=True)
    peso = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    color = models.CharField(max_length=100, blank=True, null=True)
    caracteristicas_especiales = models.TextField(blank=True, null=True)
    
    # Campos adicionales para información completa
    foto_perfil = models.ImageField(upload_to='mascotas/perfiles/', blank=True, null=True, help_text="Foto principal de la mascota")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campo para saber si ya tiene suficientes imágenes biométricas
    biometria_entrenada = models.BooleanField(default=False)
    # Confianza promedio del reconocimiento de esta mascota
    confianza_biometrica = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # campo opcional para almacenar información adicional en JSON
    metadata = models.JSONField(blank=True, null=True)
    
    # Campo para reportar mascota como perdida
    reportar_perdida = models.BooleanField(
        default=False, 
        help_text="Indica si la mascota ha sido reportada como perdida"
    )
    
    # Campos de geolocalización para mascotas perdidas/encontradas
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Latitud de la ubicación donde se reportó la mascota"
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Longitud de la ubicación donde se reportó la mascota"
    )
    ubicacion_descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Descripción de la ubicación (dirección, referencia)"
    )
    fecha_ubicacion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora cuando se registró la última ubicación"
    )
    
    def get_biometric_image_count(self):
        """Retorna el número de imágenes biométricas de la mascota"""
        return self.imagenes.filter(is_biometrica=True).count()
        
    @property
    def sexo_display(self):
        """Retorna la representación legible del sexo"""
        return self.get_sexo_display() if self.sexo else "No especificado"
        
    @property
    def etapa_vida_display(self):
        """Retorna la representación legible de la etapa de vida"""
        return self.get_etapa_vida_display() if self.etapa_vida else "No especificada"
        
    @property
    def edad_completa(self):
        """Retorna la edad completa con su unidad"""
        if self.edad is None:
            return "No especificada"
        return f"{self.edad} {self.edad_unidad}"

    def __str__(self):
        return f"{self.nombre} ({self.id})"

    @property
    def imagenes_count(self):
        return self.imagenes.count()
    
    @property
    def tiene_suficientes_imagenes(self):
        """Verifica si la mascota tiene suficientes imágenes para entrenamiento (mínimo 5)"""
        return self.imagenes.count() >= 5
    
    def save(self, *args, **kwargs):
        """Genera UUID automáticamente si no existe"""
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Retorna la URL para ver el detalle de esta mascota"""
        from django.urls import reverse
        return reverse('mascota:detalle', kwargs={'pk': self.pk})
        
    def get_qr_url(self):
        """Retorna la URL pública para el código QR"""
        from django.urls import reverse
        return reverse('mascota:qr_info', kwargs={'uuid': self.uuid})
    
    def get_recomendaciones_cuidado(self):
        """Genera recomendaciones personalizadas de cuidado basadas en los datos de la mascota"""
        recomendaciones = {
            'alimentacion': [],
            'ejercicio': [],
            'salud': [],
            'cuidado_general': []
        }
        
        # Recomendaciones por etapa de vida
        if self.etapa_vida == 'cachorro':
            recomendaciones['alimentacion'].extend([
                'Alimentación específica para cachorros con alta cantidad de proteínas',
                'Comidas pequeñas y frecuentes (3-4 veces al día)',
                'Asegurar hidratación constante'
            ])
            recomendaciones['salud'].extend([
                'Calendario de vacunación completo (muy importante)',
                'Desparasitación regular cada 2-4 semanas',
                'Visitas veterinarias mensuales para seguimiento'
            ])
            recomendaciones['ejercicio'].extend([
                'Juegos cortos y supervisados',
                'Evitar ejercicio intenso hasta completar desarrollo'
            ])
            recomendaciones['cuidado_general'].extend([
                'Socialización temprana con otros animales y personas',
                'Entrenamiento básico de comportamiento'
            ])
            
        elif self.etapa_vida == 'joven':
            recomendaciones['alimentacion'].extend([
                'Transición gradual a alimento para adultos jóvenes',
                'Control de porciones para evitar sobrepeso'
            ])
            recomendaciones['ejercicio'].extend([
                'Actividad física regular y estructurada',
                'Juegos interactivos para estimulación mental'
            ])
            recomendaciones['salud'].extend([
                'Chequeos veterinarios cada 6 meses',
                'Mantenimiento de calendario de vacunas'
            ])
            
        elif self.etapa_vida == 'adulto':
            recomendaciones['alimentacion'].extend([
                'Dieta balanceada según nivel de actividad',
                'Control de peso para mantener condición corporal óptima'
            ])
            recomendaciones['ejercicio'].extend([
                'Ejercicio regular según la raza y energía',
                'Actividades que mantengan agilidad mental'
            ])
            recomendaciones['salud'].extend([
                'Chequeos veterinarios anuales',
                'Monitoreo de signos de envejecimiento temprano'
            ])
            
        elif self.etapa_vida == 'senior':
            recomendaciones['alimentacion'].extend([
                'Dieta especializada para mascotas senior',
                'Suplementos para articulaciones si es necesario',
                'Alimentos fáciles de digerir'
            ])
            recomendaciones['ejercicio'].extend([
                'Ejercicio suave y controlado',
                'Paseos cortos pero frecuentes',
                'Evitar actividades de alto impacto'
            ])
            recomendaciones['salud'].extend([
                'Chequeos veterinarios cada 6 meses',
                'Exámenes de sangre regulares',
                'Monitoreo de artritis y otras condiciones de edad'
            ])
            recomendaciones['cuidado_general'].extend([
                'Ambiente cómodo y cálido',
                'Cama ortopédica para mayor comodidad'
            ])
        
        # Recomendaciones por estado corporal
        if self.estado_corporal == 'delgado':
            recomendaciones['alimentacion'].extend([
                'Aumentar gradualmente la cantidad de alimento',
                'Alimentos ricos en calorías y nutrientes',
                'Consultar con veterinario sobre posibles causas'
            ])
            recomendaciones['salud'].append('Descartar problemas de salud subyacentes')
            
        elif self.estado_corporal == 'obeso':
            recomendaciones['alimentacion'].extend([
                'Dieta controlada en calorías',
                'Alimentos bajos en grasa',
                'Evitar premios excesivos entre comidas'
            ])
            recomendaciones['ejercicio'].extend([
                'Incrementar gradualmente la actividad física',
                'Ejercicios de bajo impacto para articulaciones'
            ])
            recomendaciones['salud'].extend([
                'Monitoreo regular del peso',
                'Chequeos más frecuentes para detectar diabetes o problemas cardíacos'
            ])
            
        elif self.estado_corporal == 'normal':
            recomendaciones['alimentacion'].append('Mantener la dieta actual que está funcionando bien')
            recomendaciones['ejercicio'].append('Continuar con el nivel actual de actividad física')
        
        # Recomendaciones por sexo
        if self.sexo == 'hembra':
            recomendaciones['salud'].extend([
                'Considerar esterilización para prevenir enfermedades reproductivas',
                'Estar atento a signos de embarazo si no está esterilizada'
            ])
        elif self.sexo == 'macho':
            recomendaciones['salud'].append('Considerar castración para prevenir problemas de próstata')
        
        # Recomendaciones generales siempre importantes
        recomendaciones['cuidado_general'].extend([
            'Cepillado regular según tipo de pelaje',
            'Limpieza dental regular o juguetes dentales',
            'Revisión y limpieza de oídos',
            'Corte de uñas cuando sea necesario',
            'Microchip para identificación',
            'Mantener al día documentación veterinaria'
        ])
        
        # Filtrar listas vacías y eliminar duplicados
        for categoria in recomendaciones:
            recomendaciones[categoria] = list(set(recomendaciones[categoria]))
            
        return recomendaciones
    
    def delete(self, *args, **kwargs):
        """Elimina la mascota y todos sus archivos asociados"""
        # Eliminar todas las imágenes asociadas (esto activará el delete de ImagenMascota)
        for imagen in self.imagenes.all():
            imagen.delete()
            
        # Eliminar foto de perfil si existe
        if self.foto_perfil:
            try:
                # Usar storage.delete() en lugar de os.remove() para compatibilidad con Azure Storage
                if self.foto_perfil.name:
                    self.foto_perfil.storage.delete(self.foto_perfil.name)
                    print(f"Foto de perfil eliminada: {self.foto_perfil.name}")
            except Exception as e:
                print(f"Error al eliminar foto de perfil: {e}")
                
        # Llamar al delete del padre
        super().delete(*args, **kwargs)
        
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"


class ReporteMascotaEncontrada(models.Model):
    """
    Modelo para registrar reportes de mascotas encontradas.
    Permite que cualquier persona reporte haber encontrado una mascota perdida,
    sin cambiar automáticamente su estado. El propietario decide si es su mascota.
    """
    mascota = models.ForeignKey(
        'Mascota',
        on_delete=models.CASCADE,
        related_name='reportes_encontrada',
        help_text="Mascota que fue reportada como encontrada"
    )
    
    # Datos del reporte
    fecha_reporte = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora del reporte"
    )
    
    # Ubicación donde se encontró
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Latitud donde se encontró la mascota"
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Longitud donde se encontró la mascota"
    )
    ubicacion_descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Descripción de la ubicación"
    )
    
    # Foto del reporte (la imagen escaneada)
    foto_reporte = models.ImageField(
        upload_to='reportes_encontrada/',
        blank=True,
        null=True,
        help_text="Foto de la mascota al momento del reporte"
    )
    
    # Datos de quien reportó (opcional, puede ser anónimo)
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_realizados',
        help_text="Usuario que realizó el reporte (si está autenticado)"
    )
    nombre_reportante = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Nombre de quien reporta (si no está autenticado)"
    )
    telefono_reportante = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Teléfono de contacto del reportante"
    )
    email_reportante = models.EmailField(
        blank=True,
        null=True,
        help_text="Email de contacto del reportante"
    )
    
    # Información técnica del reporte
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="Dirección IP desde donde se hizo el reporte"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent del navegador"
    )
    
    # Estado del reporte
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de revisión'),
        ('confirmado', 'Confirmado por propietario'),
        ('descartado', 'Descartado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        help_text="Estado del reporte"
    )
    
    # Notas del propietario
    notas_propietario = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales del propietario"
    )
    fecha_revision = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha en que el propietario revisó el reporte"
    )
    
    # Metadata
    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Datos adicionales del reporte en formato JSON"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_reporte']
        verbose_name = 'Reporte de Mascota Encontrada'
        verbose_name_plural = 'Reportes de Mascotas Encontradas'
        indexes = [
            models.Index(fields=['mascota', 'estado']),
            models.Index(fields=['fecha_reporte']),
        ]
    
    def __str__(self):
        return f"Reporte de {self.mascota.nombre} - {self.fecha_reporte.strftime('%d/%m/%Y %H:%M')}"
    
    def confirmar(self, propietario, notas=None):
        """Marca el reporte como confirmado por el propietario"""
        self.estado = 'confirmado'
        self.fecha_revision = timezone.now()
        if notas:
            self.notas_propietario = notas
        self.save()
        
        # Marcar la mascota como encontrada
        self.mascota.reportar_perdida = False
        self.mascota.save()
    
    def descartar(self, propietario, notas=None):
        """Marca el reporte como descartado"""
        self.estado = 'descartado'
        self.fecha_revision = timezone.now()
        if notas:
            self.notas_propietario = notas
        self.save()


class ImagenMascota(models.Model):
    TIPO_CHOICES = [
        ('perfil', 'Perfil'),
        ('frontal', 'Frontal'),
        ('lateral', 'Lateral'),
        ('completo', 'Cuerpo Completo'),
        ('detalle', 'Detalle'),
        ('biometrica', 'Biométrica'),
        ('otro', 'Otro')
    ]
    
    mascota = models.ForeignKey(
        Mascota, on_delete=models.CASCADE, related_name="imagenes"
    )
    imagen = models.ImageField(upload_to=upload_to_mascota)
    uploaded_at = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='biometrica'
    )
    etiqueta = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )
    is_biometrica = models.BooleanField(
        default=True, 
        help_text="Indica si esta imagen se usa para reconocimiento biométrico"
    )
    procesada = models.BooleanField(
        default=False, 
        help_text="Indica si ya se han extraído los embeddings"
    )
    calidad = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Puntuación de calidad para biometría (0-1)"
    )
    
    def __str__(self):
        return f"Imagen {self.id} - {self.mascota.nombre} ({self.tipo})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('mascota:imagen_detalle', kwargs={'pk': self.pk})
    
    @property
    def url(self):
        """Retorna la URL de la imagen"""
        return self.imagen.url if self.imagen else None
    
    def delete(self, *args, **kwargs):
        """Elimina el archivo de imagen al eliminar el objeto"""
        if self.imagen:
            try:
                # Usar storage.delete() en lugar de os.remove() para compatibilidad con Azure Storage
                if self.imagen.name:
                    self.imagen.storage.delete(self.imagen.name)
                    print(f"Archivo eliminado: {self.imagen.name}")
            except Exception as e:
                print(f"Error al eliminar archivo de imagen {self.imagen.name}: {e}")
        super().delete(*args, **kwargs)
    
    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Imagen de Mascota"
        verbose_name_plural = "Imágenes de Mascotas"


class ModeloGlobal(models.Model):
    """
    Guarda la versión del modelo global (clasificador) que se usa para reconocimiento.
    Solo debería existir 1 registro 'activo' pero se conservan versiones históricas.
    """
    MODEL_TYPE_CHOICES = [
        ('knn', 'K-Nearest Neighbors'),
        ('svm', 'Support Vector Machine'),
        ('rf', 'Random Forest'),
        ('mlp', 'Multi-Layer Perceptron'),
        ('custom', 'Modelo Personalizado')
    ]
    
    FEATURE_EXTRACTOR_CHOICES = [
        ('efficientnet_b0', 'EfficientNet B0'),
        ('resnet50', 'ResNet 50'),
        ('mobilenet', 'MobileNet'),
        ('vgg16', 'VGG16'),
        ('other', 'Otro')
    ]
    
    nombre = models.CharField(max_length=150, default="modelo_global")
    modelo_file = models.FileField(
        upload_to=upload_to_modelos, 
        blank=True, 
        null=True,
        help_text="Archivo pickle con el modelo entrenado"
    )
    vectorizer_file = models.FileField(
        upload_to=upload_to_modelos,
        blank=True,
        null=True,
        help_text="Modelo de extracción de características (opcional)"
    )
    tipo_modelo = models.CharField(
        max_length=20,
        choices=MODEL_TYPE_CHOICES,
        default='knn',
        help_text="Algoritmo utilizado para la clasificación"
    )
    extractor_caracteristicas = models.CharField(
        max_length=30,
        choices=FEATURE_EXTRACTOR_CHOICES,
        default='efficientnet_b0',
        help_text="Modelo usado para extraer embeddings"
    )
    hiperparametros = models.JSONField(
        blank=True, 
        null=True,
        help_text="Hiperparámetros del modelo en formato JSON"
    )
    metricas = models.JSONField(
        blank=True, 
        null=True,
        help_text="Métricas de rendimiento del modelo (precisión, recall, etc.)"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)
    num_clases = models.PositiveIntegerField(
        default=0,
        help_text="Número de mascotas clasificadas por este modelo"
    )
    num_imagenes_entrenamiento = models.PositiveIntegerField(
        default=0,
        help_text="Número de imágenes usadas para entrenar este modelo"
    )
    tiempo_entrenamiento = models.FloatField(
        null=True, 
        blank=True,
        help_text="Tiempo en segundos que tomó entrenar este modelo"
    )
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_modelo}) - v{self.version}"
    
    def save(self, *args, **kwargs):
        """Al guardar un modelo como activo, desactiva los demás"""
        if self.activo:
            ModeloGlobal.objects.exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_model(cls):
        """Retorna el modelo activo o None si no hay ninguno"""
        try:
            return cls.objects.filter(activo=True).first()
        except cls.DoesNotExist:
            return None

    class Meta:
        ordering = ["-version"]
        verbose_name = "Modelo Global"
        verbose_name_plural = "Modelos Globales"


class EmbeddingStore(models.Model):
    """
    Almacena embeddings por imagen para reconocimiento biométrico.
    Permite reconstruir datasets sin reextraer las features desde las imágenes.
    """
    mascota = models.ForeignKey(
        Mascota, 
        on_delete=models.CASCADE, 
        related_name="embeddings"
    )
    imagen = models.ForeignKey(
        ImagenMascota, 
        on_delete=models.CASCADE, 
        related_name="embeddings"
    )
    # Guardamos el vector como lista serializada (JSONField)
    vector = models.JSONField(help_text="Vector de características (embedding) serializado")
    dimension = models.PositiveIntegerField(
        default=1280,
        help_text="Dimensión del vector de características"
    )
    modelo_extractor = models.CharField(
        max_length=50, 
        default="efficientnet_b0",
        help_text="Modelo usado para extraer este embedding"
    )
    crop_index = models.PositiveIntegerField(
        default=0,
        help_text="Índice del crop/augmentación (0=original, >0=crops adicionales)"
    )
    confianza = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confianza de la extracción (si aplica)"
    )
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)
    usado_en_entrenamiento = models.BooleanField(
        default=False,
        help_text="Indica si este embedding se ha usado para entrenar el modelo global"
    )
    
    def __str__(self):
        return f"Embedding {self.id} - Mascota {self.mascota.nombre}"
    
    class Meta:
        ordering = ["-creado"]
        verbose_name = "Embedding"
        verbose_name_plural = "Embeddings"
        
        
class RegistroReconocimiento(models.Model):
    """
    Registra cada intento de reconocimiento biométrico, exitoso o no.
    Útil para análisis y mejora del sistema.
    """
    fecha = models.DateTimeField(default=timezone.now)
    mascota_predicha = models.ForeignKey(
        Mascota, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='predicciones'
    )
    mascota_real = models.ForeignKey(
        Mascota, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verificaciones'
    )
    imagen_analizada = models.ImageField(
        upload_to='reconocimientos/',
        null=True,
        blank=True
    )
    confianza = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    exito = models.BooleanField(default=False)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconocimientos'
    )
    tiempo_procesamiento = models.FloatField(
        help_text="Tiempo en segundos que tomó el reconocimiento",
        null=True,
        blank=True
    )
    detalles = models.JSONField(
        null=True, 
        blank=True,
        help_text="Información adicional sobre el reconocimiento"
    )
    
    def __str__(self):
        resultado = "Exitoso" if self.exito else "Fallido"
        return f"Reconocimiento {resultado} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Registro de Reconocimiento"
        verbose_name_plural = "Registros de Reconocimientos"
