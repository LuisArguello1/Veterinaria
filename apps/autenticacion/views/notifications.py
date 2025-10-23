"""
Vistas para gestionar notificaciones del sistema
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.autenticacion.models_notification import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Vista para listar todas las notificaciones del usuario"""
    model = Notification
    template_name = 'autenticacion/notifications/list.html'
    context_object_name = 'notificaciones'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtrar solo las notificaciones del usuario actual"""
        queryset = Notification.objects.filter(
            usuario=self.request.user,
            archivada=False
        )
        
        # Filtro por tipo (opcional)
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por estado (leídas/no leídas)
        estado = self.request.GET.get('estado')
        if estado == 'no_leidas':
            queryset = queryset.filter(leida=False)
        elif estado == 'leidas':
            queryset = queryset.filter(leida=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Notificaciones'
        context['total_no_leidas'] = Notification.objects.filter(
            usuario=self.request.user,
            leida=False,
            archivada=False
        ).count()
        
        # Breadcrumb
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Notificaciones', 'url': None},
        ]
        
        return context


class NotificationMarkAsReadView(LoginRequiredMixin, View):
    """Vista para marcar una notificación como leída"""
    
    def post(self, request, pk):
        notificacion = get_object_or_404(
            Notification,
            pk=pk,
            usuario=request.user
        )
        
        notificacion.marcar_como_leida()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notificación marcada como leída'
            })
        
        messages.success(request, 'Notificación marcada como leída')
        return redirect('auth:notifications')


class NotificationMarkAllAsReadView(LoginRequiredMixin, View):
    """Vista para marcar todas las notificaciones como leídas"""
    
    def post(self, request):
        count = Notification.objects.filter(
            usuario=request.user,
            leida=False,
            archivada=False
        ).update(leida=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'count': count,
                'message': f'{count} notificaciones marcadas como leídas'
            })
        
        messages.success(request, f'{count} notificaciones marcadas como leídas')
        return redirect('auth:notifications')


class NotificationArchiveView(LoginRequiredMixin, View):
    """Vista para archivar una notificación"""
    
    def post(self, request, pk):
        notificacion = get_object_or_404(
            Notification,
            pk=pk,
            usuario=request.user
        )
        
        notificacion.archivar()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notificación archivada'
            })
        
        messages.success(request, 'Notificación archivada')
        return redirect('auth:notifications')


class NotificationDeleteView(LoginRequiredMixin, View):
    """Vista para eliminar una notificación"""
    
    def post(self, request, pk):
        notificacion = get_object_or_404(
            Notification,
            pk=pk,
            usuario=request.user
        )
        
        notificacion.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notificación eliminada'
            })
        
        messages.success(request, 'Notificación eliminada')
        return redirect('auth:notifications')


class NotificationCountView(LoginRequiredMixin, View):
    """Vista API para obtener el conteo de notificaciones no leídas"""
    
    def get(self, request):
        count = Notification.objects.filter(
            usuario=request.user,
            leida=False,
            archivada=False
        ).count()
        
        return JsonResponse({
            'count': count,
            'has_notifications': count > 0
        })


class NotificationRecentView(LoginRequiredMixin, View):
    """Vista API para obtener las notificaciones recientes (para dropdown)"""
    
    def get(self, request):
        limit = int(request.GET.get('limit', 5))
        
        notificaciones = Notification.objects.filter(
            usuario=request.user,
            archivada=False
        )[:limit]
        
        data = {
            'notificaciones': [
                {
                    'id': n.id,
                    'titulo': n.titulo,
                    'mensaje': n.mensaje[:100] + '...' if len(n.mensaje) > 100 else n.mensaje,
                    'tipo': n.tipo,
                    'icono': n.icono,
                    'leida': n.leida,
                    'tiempo': n.tiempo_transcurrido,
                    'url_accion': n.url_accion,
                    'texto_accion': n.texto_accion,
                }
                for n in notificaciones
            ],
            'total': Notification.objects.filter(
                usuario=request.user,
                leida=False,
                archivada=False
            ).count()
        }
        
        return JsonResponse(data)
