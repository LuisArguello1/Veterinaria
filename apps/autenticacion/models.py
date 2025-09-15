from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

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