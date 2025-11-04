from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class User(AbstractUser):
    # Opciones de roles
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrador')
        OWNER = 'OWNER', _('Dueño')
        VET = 'VET', _('Veterinario')
    
    # Campos adicionales
    dni = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="Cédula")
    image = models.ImageField(upload_to='users/', null=True, blank=True, verbose_name="Foto de perfil")
    direction = models.CharField(max_length=255, null=True, blank=True, verbose_name="Dirección")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="Teléfono")
    
    # Campo de rol
    role = models.CharField(
        max_length=5,
        choices=Role.choices,
        default=Role.OWNER,
        verbose_name="Rol"
    )
    
    # Para veterinarios
    specialization = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Especialización"
    )

    license_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name="Número de licencia"
    )
    
    email = models.EmailField('Email', unique=True)
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_owner(self):
        return self.role == self.Role.OWNER
    
    @property
    def is_vet(self):
        return self.role == self.Role.VET

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/usuario_anonimo.webp'


class UserFaceEmbedding(models.Model):
    """Modelo para almacenar embeddings faciales de usuarios para autenticación biométrica con ArcFace"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='face_embedding',
        verbose_name="Usuario"
    )
    
    # Embedding facial de ArcFace (512 dimensiones)
    embedding_vector = models.JSONField(
        default=list,
        verbose_name="Vector de embedding",
        help_text="Vector de 512 dimensiones generado por ArcFace ResNet100"
    )
    
    embedding_size = models.IntegerField(
        default=512,
        verbose_name="Tamaño del embedding",
        help_text="Número de dimensiones del vector (512 para ArcFace)"
    )
    
    model_version = models.CharField(
        max_length=50,
        default="arcfaceresnet100-8",
        verbose_name="Versión del modelo",
        help_text="Versión del modelo ArcFace utilizado"
    )
    
    # Metadatos de la captura
    confidence_score = models.FloatField(
        default=0.0,
        verbose_name="Puntuación de confianza",
        help_text="Calidad del rostro detectado por YuNet (0.0 - 1.0)"
    )
    
    face_bbox = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Coordenadas del rostro",
        help_text="Coordenadas (x, y, w, h) del rostro detectado"
    )
    
    # Estado y permisos
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    allow_login = models.BooleanField(
        default=True,
        verbose_name="Permitir login facial"
    )
    
    # Estadísticas de uso
    successful_logins = models.PositiveIntegerField(
        default=0,
        verbose_name="Logins exitosos"
    )
    
    failed_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos fallidos"
    )
    
    last_successful_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último login exitoso"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    class Meta:
        verbose_name = "Descriptor Facial"
        verbose_name_plural = "Descriptores Faciales"
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['last_successful_login']),
        ]
    
    def __str__(self):
        status = "✓ Activo" if self.is_active else "✗ Inactivo"
        return f"Biometría de {self.user.username} - {status}"
    
    def increment_successful_login(self):
        """Incrementa el contador de logins exitosos"""
        self.successful_logins += 1
        self.last_successful_login = timezone.now()
        self.failed_attempts = 0
        self.save()
    
    def increment_failed_attempt(self):
        """Incrementa el contador de intentos fallidos"""
        self.failed_attempts += 1
        self.save()
    
    @property
    def login_enabled(self):
        """Verifica si el login facial está habilitado"""
        return self.is_active and self.allow_login


class Notification(models.Model):
    """
    Modelo para gestionar notificaciones del sistema.
    Permite crear notificaciones dinámicamente basadas en acciones del sistema.
    """
    
    class NotificationType(models.TextChoices):
        INFO = 'INFO', 'Información'
        SUCCESS = 'SUCCESS', 'Éxito'
        WARNING = 'WARNING', 'Advertencia'
        ERROR = 'ERROR', 'Error'
        ALERT = 'ALERT', 'Alerta'
    
    class NotificationCategory(models.TextChoices):
        SYSTEM = 'SYSTEM', 'Sistema'
        MASCOTA = 'MASCOTA', 'Mascota'
        USUARIO = 'USUARIO', 'Usuario'
        BIOMETRIA = 'BIOMETRIA', 'Biometría'
        PERDIDA = 'PERDIDA', 'Mascota Perdida'
        ENCONTRADA = 'ENCONTRADA', 'Mascota Encontrada'
        VACUNA = 'VACUNA', 'Vacunación'
        CONSULTA = 'CONSULTA', 'Consulta Veterinaria'
        OTRO = 'OTRO', 'Otro'
    
    # Usuario destinatario
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Usuario"
    )
    
    # Tipo y categoría
    notification_type = models.CharField(
        max_length=10,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name="Tipo de notificación"
    )
    
    category = models.CharField(
        max_length=15,
        choices=NotificationCategory.choices,
        default=NotificationCategory.SYSTEM,
        verbose_name="Categoría"
    )
    
    # Contenido
    title = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    
    message = models.TextField(
        verbose_name="Mensaje"
    )
    
    # Relación genérica (para asociar con cualquier modelo)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Tipo de contenido"
    )
    
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID del objeto"
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # URL de acción (opcional)
    action_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="URL de acción",
        help_text="URL a la que redirigir al hacer clic en la notificación"
    )
    
    # Estado
    is_read = models.BooleanField(
        default=False,
        verbose_name="Leída"
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de lectura"
    )
    
    # Metadatos adicionales (JSON para flexibilidad)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos adicionales"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de expiración",
        help_text="Fecha después de la cual la notificación se considera obsoleta"
    )
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f"{status} {self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Marca la notificación como no leída"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """Verifica si la notificación ha expirado"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def age_in_days(self):
        """Retorna la edad de la notificación en días"""
        return (timezone.now() - self.created_at).days
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type=NotificationType.INFO, 
                          category=NotificationCategory.SYSTEM, action_url=None, 
                          content_object=None, metadata=None, expires_in_days=None):
        """
        Método helper para crear notificaciones fácilmente
        
        Args:
            user: Usuario destinatario
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación (INFO, SUCCESS, WARNING, ERROR, ALERT)
            category: Categoría de la notificación
            action_url: URL opcional para acción
            content_object: Objeto relacionado opcional
            metadata: Diccionario con metadatos adicionales
            expires_in_days: Días hasta que expire (None = sin expiración)
        
        Returns:
            Notification: Instancia de la notificación creada
        """
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        
        notification = cls(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            action_url=action_url,
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        if content_object:
            notification.content_object = content_object
        
        notification.save()
        return notification
    
    @classmethod
    def get_unread_count(cls, user):
        """Retorna el número de notificaciones no leídas para un usuario"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def get_recent_notifications(cls, user, limit=10):
        """Retorna las notificaciones más recientes para un usuario"""
        return cls.objects.filter(user=user).order_by('-created_at')[:limit]
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Marca todas las notificaciones de un usuario como leídas"""
        return cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    @classmethod
    def delete_old_notifications(cls, days=30):
        """
        Elimina notificaciones antiguas leídas
        
        Args:
            days: Días de antigüedad para eliminar (default: 30)
        
        Returns:
            int: Número de notificaciones eliminadas
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        count, _ = cls.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        ).delete()
        return count
    
    @classmethod
    def delete_expired_notifications(cls):
        """
        Elimina notificaciones expiradas
        
        Returns:
            int: Número de notificaciones eliminadas
        """
        count, _ = cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        return count

