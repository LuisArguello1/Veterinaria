from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from zoneinfo import ZoneInfo
from apps.autenticacion.models import Notification


class NotificationListView(View):
    """Vista para listar las notificaciones del usuario"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'notifications': [], 'unread_count': 0})
            
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]  # Últimas 20 notificaciones
        
        # Zona horaria de Ecuador
        tz_ecuador = ZoneInfo('America/Guayaquil')
        
        data = {
            'notifications': [
                {
                    'id': n.id,
                    'title': n.title,
                    'message': n.message,
                    'notification_type': n.notification_type,
                    'category': n.category,
                    'is_read': n.is_read,
                    'action_url': n.action_url,
                    'created_at': n.created_at.astimezone(tz_ecuador).isoformat(),
                }
                for n in notifications
            ],
            'unread_count': Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
        
        return JsonResponse(data)


class NotificationCountView(View):
    """Vista para obtener el contador de notificaciones no leídas"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'unread_count': 0})
            
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({'unread_count': unread_count})


class NotificationMarkReadView(View):
    """Vista para marcar una notificación como leída"""
    
    def post(self, request, notification_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'No autenticado'}, status=401)
            
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.mark_as_read()
            
            return JsonResponse({
                'success': True,
                'message': 'Notificación marcada como leída'
            })
        except Notification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Notificación no encontrada'
            }, status=404)


class NotificationMarkAllReadView(View):
    """Vista para marcar todas las notificaciones como leídas"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'No autenticado'}, status=401)
            
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notificaciones marcadas como leídas',
            'count': count
        })


class NotificationDeleteView(View):
    """Vista para eliminar una notificación"""
    
    def delete(self, request, notification_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'No autenticado'}, status=401)
            
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Notificación eliminada'
            })
        except Notification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Notificación no encontrada'
            }, status=404)
