"""
Ejemplos de cómo crear notificaciones en el sistema

Importa las funciones helper:
from apps.autenticacion.utils.notifications_helper import (
    notify_user, notify_success, notify_warning, notify_error,
    notify_mascota, notify_security, notify_veterinary
)

O usa el método del modelo:
from apps.autenticacion.models import Notification
"""

# EJEMPLO 1: Notificación simple al registrar un usuario
def ejemplo_registro_usuario(user):
    from apps.autenticacion.utils.notifications_helper import notify_success
    
    notify_success(
        user=user,
        title="¡Bienvenido a PET FACE ID!",
        message="Tu cuenta ha sido creada exitosamente. Ahora puedes registrar tus mascotas.",
        category='USER',
        action_url='/mascota/main-register/'
    )


# EJEMPLO 2: Notificación al registrar una mascota
def ejemplo_registro_mascota(user, mascota):
    from apps.autenticacion.utils.notifications_helper import notify_mascota
    
    notify_mascota(
        user=user,
        title=f"¡{mascota.name} ha sido registrada!",
        message=f"Tu mascota {mascota.name} ha sido registrada exitosamente en el sistema.",
        mascota=mascota,
        notification_type='SUCCESS',
        action_url=f'/mascota/{mascota.id}/'
    )


# EJEMPLO 3: Notificación de seguridad (login facial)
def ejemplo_login_facial_exitoso(user):
    from apps.autenticacion.utils.notifications_helper import notify_security
    
    notify_security(
        user=user,
        title="Inicio de sesión facial detectado",
        message="Se ha detectado un inicio de sesión mediante reconocimiento facial.",
        notification_type='INFO',
        metadata={
            'ip_address': '192.168.1.1',
            'device': 'Chrome on Windows'
        }
    )


# EJEMPLO 4: Notificación de mascota perdida
def ejemplo_mascota_perdida(user, mascota):
    from apps.autenticacion.utils.notifications_helper import notify_mascota
    
    notify_mascota(
        user=user,
        title=f"¡{mascota.name} ha sido marcada como perdida!",
        message=f"Tu mascota {mascota.name} ha sido reportada como perdida. La comunidad será notificada.",
        mascota=mascota,
        notification_type='WARNING',
        action_url=f'/mascota/{mascota.id}/'
    )


# EJEMPLO 5: Notificación de mascota encontrada
def ejemplo_mascota_encontrada(user, mascota, ubicacion):
    from apps.autenticacion.utils.notifications_helper import notify_mascota
    
    notify_mascota(
        user=user,
        title=f"¡Alguien encontró a {mascota.name}!",
        message=f"Tu mascota {mascota.name} ha sido escaneada en {ubicacion}. Revisa los detalles.",
        mascota=mascota,
        notification_type='SUCCESS',
        action_url=f'/mascota/{mascota.id}/',
        metadata={
            'ubicacion': ubicacion,
            'fecha_escaneo': '2025-11-03 14:30:00'
        }
    )


# EJEMPLO 6: Notificación veterinaria
def ejemplo_consulta_veterinaria(user, mascota, veterinario):
    from apps.autenticacion.utils.notifications_helper import notify_veterinary
    
    notify_veterinary(
        user=user,
        title="Nueva consulta veterinaria registrada",
        message=f"Se ha registrado una nueva consulta para {mascota.name} con {veterinario.get_full_name()}.",
        notification_type='INFO',
        action_url=f'/mascota/{mascota.id}/',
        metadata={
            'veterinario': veterinario.get_full_name(),
            'mascota': mascota.name
        }
    )


# EJEMPLO 7: Notificación de error
def ejemplo_error_sistema(user):
    from apps.autenticacion.utils.notifications_helper import notify_error
    
    notify_error(
        user=user,
        title="Error al procesar tu solicitud",
        message="Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde.",
        category='SYSTEM'
    )


# EJEMPLO 8: Notificación con expiración
def ejemplo_notificacion_temporal(user):
    from apps.autenticacion.models import Notification
    
    Notification.create_notification(
        user=user,
        title="Oferta especial",
        message="Aprovecha nuestra oferta especial por tiempo limitado.",
        notification_type=Notification.NotificationType.INFO,
        category=Notification.NotificationCategory.OTHER,
        expires_in_days=7
    )


# EJEMPLO 9: Notificar a múltiples usuarios
def ejemplo_notificar_multiples_usuarios(usuarios):
    from apps.autenticacion.utils.notifications_helper import notify_user
    
    for user in usuarios:
        notify_user(
            user=user,
            title="Mantenimiento programado",
            message="El sistema estará en mantenimiento el día 10 de noviembre de 2:00 AM a 4:00 AM.",
            category='SYSTEM'
        )


# EJEMPLO 10: Usar el modelo directamente
def ejemplo_modelo_directo(user):
    from apps.autenticacion.models import Notification
    
    Notification.objects.create(
        user=user,
        title="Notificación personalizada",
        message="Este es un mensaje personalizado.",
        notification_type=Notification.NotificationType.INFO,
        category=Notification.NotificationCategory.SYSTEM,
        action_url='/dashboard/',
        metadata={
            'custom_field': 'custom_value',
            'priority': 'high'
        }
    )
