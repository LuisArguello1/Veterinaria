from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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
    """Modelo para almacenar descriptores faciales de usuarios para autenticación biométrica"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='face_embedding',
        verbose_name="Usuario"
    )
    
    # Descriptor facial serializado como JSON
    descriptor_data = models.TextField(
        default='{}',
        verbose_name="Descriptor facial",
        help_text="Descriptor facial (LBP + textura + geométrico) como JSON"
    )
    
    # Metadatos de la captura
    confidence_score = models.FloatField(
        default=0.0,
        verbose_name="Puntuación de confianza",
        help_text="Calidad del rostro detectado (0.0 - 1.0)"
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
