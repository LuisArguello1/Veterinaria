"""
Modelo de Historial Médico para Mascotas
Incluye vacunas, citas, tratamientos y recordatorios automáticos
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.mascota.models import Mascota
from apps.autenticacion.models import User


class HistorialMedico(models.Model):
    """Historial médico completo de la mascota"""
    
    TIPO_EVENTO_CHOICES = [
        ('vacuna', 'Vacunación'),
        ('desparasitacion', 'Desparasitación'),
        ('consulta', 'Consulta Veterinaria'),
        ('cirugia', 'Cirugía'),
        ('tratamiento', 'Tratamiento'),
        ('revision', 'Revisión General'),
        ('emergencia', 'Emergencia'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('reprogramado', 'Reprogramado'),
    ]
    
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='historial_medico'
    )
    
    veterinario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'VET'},
        related_name='consultas_realizadas'
    )
    
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Fechas
    fecha_evento = models.DateField()
    fecha_proxima = models.DateField(null=True, blank=True, help_text="Fecha de próxima vacuna/revisión")
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='completado')
    
    # Detalles adicionales
    medicamentos = models.TextField(blank=True, help_text="Medicamentos recetados")
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)
    
    # Archivo adjunto (ej: resultados de laboratorio)
    archivo_adjunto = models.FileField(
        upload_to='historial_medico/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Recordatorios
    recordatorio_enviado = models.BooleanField(default=False)
    dias_anticipacion_recordatorio = models.IntegerField(
        default=7,
        help_text="Días de anticipación para enviar recordatorio"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_evento']
        verbose_name = 'Historial Médico'
        verbose_name_plural = 'Historiales Médicos'
        indexes = [
            models.Index(fields=['mascota', '-fecha_evento']),
            models.Index(fields=['fecha_proxima', 'recordatorio_enviado']),
        ]
    
    def __str__(self):
        return f"{self.mascota.nombre} - {self.get_tipo_evento_display()} - {self.fecha_evento}"
    
    def save(self, *args, **kwargs):
        """Crear notificación automática al crear un evento"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self._crear_notificacion_nuevo_evento()
    
    def _crear_notificacion_nuevo_evento(self):
        """Notificar al propietario sobre el nuevo evento médico"""
        from apps.autenticacion.models_notification import Notification
        
        mensaje = f"Se ha registrado: {self.titulo} para {self.mascota.nombre}"
        if self.fecha_proxima:
            mensaje += f". Próxima cita: {self.fecha_proxima.strftime('%d/%m/%Y')}"
        
        Notification.crear_notificacion(
            usuario=self.mascota.propietario,
            titulo=f"📋 {self.get_tipo_evento_display()} Registrada",
            mensaje=mensaje,
            tipo='INFO',
            icono='pi-file-medical',
            url_accion=f'/mascota/{self.mascota.pk}/',
            texto_accion='Ver detalles de la mascota'
        )
    
    def enviar_recordatorio_si_corresponde(self):
        """Enviar recordatorio si la fecha próxima está cerca"""
        if not self.fecha_proxima or self.recordatorio_enviado:
            return False
        
        dias_restantes = (self.fecha_proxima - timezone.now().date()).days
        
        if dias_restantes <= self.dias_anticipacion_recordatorio and dias_restantes >= 0:
            self._enviar_recordatorio()
            return True
        
        return False
    
    def _enviar_recordatorio(self):
        """Enviar notificación de recordatorio"""
        from apps.autenticacion.models_notification import Notification
        
        dias_restantes = (self.fecha_proxima - timezone.now().date()).days
        
        if dias_restantes == 0:
            tiempo_texto = "¡HOY!"
        elif dias_restantes == 1:
            tiempo_texto = "mañana"
        else:
            tiempo_texto = f"en {dias_restantes} días"
        
        icono_por_tipo = {
            'vacuna': 'pi-shield',
            'desparasitacion': 'pi-sun',
            'consulta': 'pi-calendar',
            'revision': 'pi-check-circle',
        }
        
        Notification.crear_notificacion(
            usuario=self.mascota.propietario,
            titulo=f"🔔 Recordatorio: {self.titulo}",
            mensaje=f"La {self.get_tipo_evento_display().lower()} de {self.mascota.nombre} está programada para {tiempo_texto} ({self.fecha_proxima.strftime('%d/%m/%Y')})",
            tipo='REMINDER',
            icono=icono_por_tipo.get(self.tipo_evento, 'pi-bell'),
            url_accion=f'/mascota/{self.mascota.pk}/',
            texto_accion='Ver historial médico'
        )
        
        self.recordatorio_enviado = True
        self.save(update_fields=['recordatorio_enviado'])
    
    @classmethod
    def verificar_recordatorios_pendientes(cls):
        """
        Método para ejecutar periódicamente (cron job)
        Verifica todos los recordatorios pendientes
        """
        eventos_pendientes = cls.objects.filter(
            fecha_proxima__isnull=False,
            recordatorio_enviado=False,
            estado='pendiente'
        )
        
        count = 0
        for evento in eventos_pendientes:
            if evento.enviar_recordatorio_si_corresponde():
                count += 1
        
        return count


class Vacuna(models.Model):
    """Modelo específico para vacunas (catálogo)"""
    
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)
    frecuencia_meses = models.IntegerField(
        help_text="Cada cuántos meses se debe aplicar (ej: 12 para anual)"
    )
    edad_minima_meses = models.IntegerField(
        default=2,
        help_text="Edad mínima en meses para aplicar esta vacuna"
    )
    
    # Para mascotas específicas
    apta_para_perros = models.BooleanField(default=True)
    apta_para_gatos = models.BooleanField(default=True)
    apta_para_otras = models.BooleanField(default=False)
    
    obligatoria = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Vacuna'
        verbose_name_plural = 'Vacunas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def calcular_proxima_fecha(self, fecha_aplicacion):
        """Calcular fecha de próxima aplicación"""
        from datetime import timedelta
        dias = self.frecuencia_meses * 30  # Aproximación
        return fecha_aplicacion + timedelta(days=dias)


class RegistroVacuna(models.Model):
    """Registro de vacunas aplicadas a mascotas"""
    
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='vacunas_aplicadas'
    )
    
    vacuna = models.ForeignKey(
        Vacuna,
        on_delete=models.CASCADE,
        related_name='aplicaciones'
    )
    
    fecha_aplicacion = models.DateField()
    fecha_proxima = models.DateField(null=True, blank=True)
    
    lote = models.CharField(max_length=100, blank=True)
    veterinario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'VET'}
    )
    
    notas = models.TextField(blank=True)
    recordatorio_enviado = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Vacuna'
        verbose_name_plural = 'Registros de Vacunas'
        ordering = ['-fecha_aplicacion']
    
    def __str__(self):
        return f"{self.mascota.nombre} - {self.vacuna.nombre} - {self.fecha_aplicacion}"
    
    def save(self, *args, **kwargs):
        """Auto-calcular fecha próxima y enviar notificación"""
        # Calcular fecha próxima si no está definida
        if not self.fecha_proxima and self.vacuna:
            self.fecha_proxima = self.vacuna.calcular_proxima_fecha(self.fecha_aplicacion)
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self._crear_notificacion_vacuna()
    
    def _crear_notificacion_vacuna(self):
        """Notificar al propietario sobre la vacuna aplicada"""
        from apps.autenticacion.models_notification import Notification
        
        mensaje = f"Se ha aplicado la vacuna '{self.vacuna.nombre}' a {self.mascota.nombre}"
        if self.fecha_proxima:
            mensaje += f". Próxima dosis: {self.fecha_proxima.strftime('%d/%m/%Y')}"
        
        Notification.crear_notificacion(
            usuario=self.mascota.propietario,
            titulo=f"💉 Vacuna Aplicada: {self.vacuna.nombre}",
            mensaje=mensaje,
            tipo='SUCCESS',
            icono='pi-shield',
            url_accion=f'/mascota/{self.mascota.pk}/',
            texto_accion='Ver cartilla de vacunación'
        )
