"""
Modelo de Notificaciones para el sistema PetFace ID
Gestiona notificaciones basadas en roles: ADMIN, VET, OWNER
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """Modelo para gestionar notificaciones del sistema"""
    
    TIPO_CHOICES = [
        ('INFO', 'Información'),
        ('SUCCESS', 'Éxito'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('REMINDER', 'Recordatorio'),
        ('SYSTEM', 'Sistema'),
    ]
    
    # Usuario destinatario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    
    # Contenido de la notificación
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='INFO')
    
    # Icono de PrimeIcons (opcional, se asigna automáticamente según el tipo)
    icono = models.CharField(max_length=50, blank=True)
    
    # URL de acción (opcional)
    url_accion = models.CharField(max_length=255, blank=True, null=True)
    texto_accion = models.CharField(max_length=100, blank=True, null=True)
    
    # Estado
    leida = models.BooleanField(default=False)
    archivada = models.BooleanField(default=False)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)  # Para datos adicionales
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['usuario', '-fecha_creacion']),
            models.Index(fields=['usuario', 'leida']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    def save(self, *args, **kwargs):
        """Asignar ícono automáticamente si no está definido"""
        if not self.icono:
            iconos_por_tipo = {
                'INFO': 'pi-info-circle',
                'SUCCESS': 'pi-check-circle',
                'WARNING': 'pi-exclamation-triangle',
                'ERROR': 'pi-times-circle',
                'REMINDER': 'pi-bell',
                'SYSTEM': 'pi-cog',
            }
            self.icono = iconos_por_tipo.get(self.tipo, 'pi-info-circle')
        
        super().save(*args, **kwargs)
    
    def marcar_como_leida(self):
        """Marcar la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])
    
    def archivar(self):
        """Archivar la notificación"""
        self.archivada = True
        self.save(update_fields=['archivada'])
    
    @property
    def tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido desde la creación"""
        from django.utils.timesince import timesince
        return timesince(self.fecha_creacion)
    
    @classmethod
    def crear_notificacion(cls, usuario, titulo, mensaje, tipo='INFO', **kwargs):
        """Método helper para crear notificaciones fácilmente"""
        return cls.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            **kwargs
        )
    
    @classmethod
    def notificar_admins(cls, titulo, mensaje, tipo='SYSTEM', **kwargs):
        """Enviar notificación a todos los ADMIN"""
        from apps.autenticacion.models import User
        admins = User.objects.filter(role='ADMIN', is_active=True)
        
        notificaciones = []
        for admin in admins:
            notificaciones.append(
                cls.crear_notificacion(admin, titulo, mensaje, tipo, **kwargs)
            )
        return notificaciones
    
    @classmethod
    def notificar_veterinarios(cls, titulo, mensaje, tipo='INFO', **kwargs):
        """Enviar notificación a todos los VET"""
        from apps.autenticacion.models import User
        veterinarios = User.objects.filter(role='VET', is_active=True)
        
        notificaciones = []
        for vet in veterinarios:
            notificaciones.append(
                cls.crear_notificacion(vet, titulo, mensaje, tipo, **kwargs)
            )
        return notificaciones
