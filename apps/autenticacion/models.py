from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# Importar el modelo de notificaciones
from .models_notification import Notification

class CustomUserManager(BaseUserManager):
    """Manager personalizado para el modelo User"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """Crear y guardar un usuario regular"""
        if not email:
            raise ValueError('El email es obligatorio')
        if not username:
            raise ValueError('El username es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Crear y guardar un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)

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
    
    # Usar el manager personalizado
    objects = CustomUserManager()
    
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