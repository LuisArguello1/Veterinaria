from apps.autenticacion.models import Notification, User
from django.contrib.contenttypes.models import ContentType


def create_notification(
    user,
    title,
    message,
    notification_type=Notification.NotificationType.INFO,
    category=Notification.NotificationCategory.SYSTEM,
    action_url=None,
    related_object=None,
    metadata=None
):
    """
    Función helper para crear notificaciones fácilmente
    
    Args:
        user: Usuario destinatario (User instance o ID)
        title: Título de la notificación
        message: Mensaje de la notificación
        notification_type: Tipo (INFO, SUCCESS, WARNING, ERROR)
        category: Categoría (SYSTEM, MASCOTA, USER, SECURITY, VETERINARY, OTHER)
        action_url: URL opcional para acción
        related_object: Objeto relacionado (mascota, usuario, etc.)
        metadata: Diccionario con metadatos adicionales
    
    Returns:
        Notification instance
    """
    if isinstance(user, int):
        user = User.objects.get(id=user)
    
    notification_data = {
        'user': user,
        'title': title,
        'message': message,
        'notification_type': notification_type,
        'category': category,
        'action_url': action_url,
    }
    
    # Si hay objeto relacionado, agregarlo
    if related_object:
        notification_data['content_type'] = ContentType.objects.get_for_model(related_object)
        notification_data['object_id'] = related_object.id
    
    # Agregar metadatos si existen
    if metadata:
        notification_data['metadata'] = metadata
    
    notification = Notification.objects.create(**notification_data)
    return notification


def notify_user(user, title, message, **kwargs):
    """Shortcut para crear una notificación INFO simple"""
    return create_notification(user, title, message, notification_type=Notification.NotificationType.INFO, **kwargs)


def notify_success(user, title, message, **kwargs):
    """Shortcut para crear una notificación SUCCESS"""
    return create_notification(user, title, message, notification_type=Notification.NotificationType.SUCCESS, **kwargs)


def notify_warning(user, title, message, **kwargs):
    """Shortcut para crear una notificación WARNING"""
    return create_notification(user, title, message, notification_type=Notification.NotificationType.WARNING, **kwargs)


def notify_error(user, title, message, **kwargs):
    """Shortcut para crear una notificación ERROR"""
    return create_notification(user, title, message, notification_type=Notification.NotificationType.ERROR, **kwargs)


# Notificaciones específicas por categoría
def notify_mascota(user, title, message, mascota=None, **kwargs):
    """Notificación relacionada con mascotas"""
    return create_notification(
        user, title, message,
        category=Notification.NotificationCategory.MASCOTA,
        related_object=mascota,
        **kwargs
    )


def notify_security(user, title, message, **kwargs):
    """Notificación de seguridad"""
    return create_notification(
        user, title, message,
        notification_type=Notification.NotificationType.WARNING,
        category=Notification.NotificationCategory.SYSTEM,
        **kwargs
    )


def notify_veterinary(user, title, message, **kwargs):
    """Notificación veterinaria"""
    return create_notification(
        user, title, message,
        category='VETERINARY',
        **kwargs
    )
