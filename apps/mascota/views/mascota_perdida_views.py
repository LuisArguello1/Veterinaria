"""
Vistas para el sistema de mascotas perdidas
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import json

from ..models import Mascota
from ..services.mascota_perdida_service import MascotaPerdidaService

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Obtiene la IP del cliente de forma segura"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
@require_http_methods(["POST"])
def reportar_perdida(request, mascota_id):
    """
    Permite al propietario reportar su mascota como perdida
    """
    try:
        mascota = get_object_or_404(Mascota, id=mascota_id)
        
        # Verificar permisos
        puede_reportar, mensaje_verificacion = MascotaPerdidaService.verificar_puede_reportar_perdida(
            mascota, request.user
        )
        
        if not puede_reportar:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': mensaje_verificacion
                }, status=403)
            
            messages.error(request, mensaje_verificacion)
            return redirect('mascota:main_register')
        
        # Obtener ubicación opcional del POST
        ubicacion_perdida = request.POST.get('ubicacion_perdida', '').strip()
        
        # Reportar como perdida
        exito, mensaje = MascotaPerdidaService.reportar_como_perdida(
            mascota, request.user, ubicacion_perdida
        )
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': exito,
                'message' if exito else 'error': mensaje,
                'mascota_nombre': mascota.nombre,
                'mascota_perdida': mascota.reportar_perdida
            })
        
        if exito:
            messages.success(request, mensaje)
        else:
            messages.error(request, mensaje)
        
        return redirect('mascota:main_register')
        
    except Exception as e:
        logger.error(f"Error en reportar_perdida: {str(e)}")
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=500)
        
        messages.error(request, 'Error interno del servidor')
        return redirect('mascota:main_register')


@login_required
@require_http_methods(["POST"])
def cancelar_reporte_perdida(request, mascota_id):
    """
    Permite al propietario cancelar el reporte de mascota perdida
    """
    try:
        mascota = get_object_or_404(Mascota, id=mascota_id)
        
        # Cancelar reporte
        exito, mensaje = MascotaPerdidaService.cancelar_reporte_perdida(mascota, request.user)
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': exito,
                'message' if exito else 'error': mensaje,
                'mascota_nombre': mascota.nombre,
                'mascota_perdida': mascota.reportar_perdida
            })
        
        if exito:
            messages.success(request, mensaje)
        else:
            messages.error(request, mensaje)
        
        return redirect('mascota:main_register')
        
    except Exception as e:
        logger.error(f"Error en cancelar_reporte_perdida: {str(e)}")
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=500)
        
        messages.error(request, 'Error interno del servidor')
        return redirect('mascota:main_register')


@require_http_methods(["POST"])
@csrf_exempt  # Para permitir acceso desde el scanner público
def reportar_encontrada(request, mascota_uuid):
    """
    Permite reportar una mascota como encontrada usando su UUID (desde QR público)
    No requiere autenticación para facilitar reportes desde cualquier dispositivo
    """
    try:
        mascota = get_object_or_404(Mascota, uuid=mascota_uuid)
        
        # Verificar que se puede reportar como encontrada
        puede_reportar, mensaje_verificacion = MascotaPerdidaService.verificar_puede_reportar_encontrada(mascota)
        
        if not puede_reportar:
            return JsonResponse({
                'success': False,
                'error': mensaje_verificacion
            }, status=400)
        
        # Obtener datos del request
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Obtener datos de ubicación del JSON si están presentes
        ubicacion_data = None
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
                ubicacion_data = body.get('ubicacion')
                logger.info(f"📍 Ubicación recibida para {mascota.nombre}: {ubicacion_data}")
        except (json.JSONDecodeError, AttributeError):
            logger.debug("No se encontraron datos de ubicación en el request")
        
        # Reportar como encontrada
        exito, mensaje = MascotaPerdidaService.reportar_como_encontrada(
            mascota, ip_address, user_agent, ubicacion_data
        )
        
        return JsonResponse({
            'success': exito,
            'message' if exito else 'error': mensaje,
            'mascota_nombre': mascota.nombre,
            'propietario_nombre': mascota.propietario.get_full_name() or mascota.propietario.username
        })
        
    except Exception as e:
        logger.error(f"Error en reportar_encontrada: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@require_http_methods(["GET"])
def verificar_estado_perdida(request, mascota_uuid):
    """
    Verifica si una mascota está reportada como perdida (para el scanner/QR público)
    """
    try:
        mascota = get_object_or_404(Mascota, uuid=mascota_uuid)
        
        return JsonResponse({
            'success': True,
            'mascota_perdida': mascota.reportar_perdida,
            'mascota_nombre': mascota.nombre,
            'puede_reportar_encontrada': mascota.reportar_perdida
        })
        
    except Mascota.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mascota no encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f"Error en verificar_estado_perdida: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@login_required
def listar_mascotas_perdidas(request):
    """
    Lista todas las mascotas reportadas como perdidas
    """
    try:
        mascotas_perdidas = MascotaPerdidaService.obtener_mascotas_perdidas(request.user)
        
        context = {
            'mascotas_perdidas': mascotas_perdidas,
            'titulo': 'Mascotas Perdidas',
            'total_perdidas': mascotas_perdidas.count()
        }
        
        return render(request, 'mascota/perdidas/lista.html', context)
        
    except Exception as e:
        logger.error(f"Error en listar_mascotas_perdidas: {str(e)}")
        messages.error(request, 'Error cargando la lista de mascotas perdidas')
        return redirect('mascota:main_register')


@require_http_methods(["GET"])
def api_mascotas_perdidas(request):
    """
    API para obtener la lista de mascotas perdidas en formato JSON
    """
    try:
        mascotas_perdidas = MascotaPerdidaService.obtener_mascotas_perdidas()
        
        data = []
        for mascota in mascotas_perdidas:
            data.append({
                'id': mascota.id,
                'uuid': str(mascota.uuid),
                'nombre': mascota.nombre,
                'raza': mascota.raza or 'No especificada',
                'color': mascota.color or 'No especificado',
                'edad': mascota.edad_completa,
                'foto_url': mascota.foto_perfil.url if mascota.foto_perfil else None,
                'propietario': {
                    'nombre': mascota.propietario.get_full_name() or mascota.propietario.username,
                    'email': mascota.propietario.email if request.user.is_authenticated else None,
                    'telefono': getattr(mascota.propietario, 'phone', None) if request.user.is_authenticated else None
                },
                'fecha_reporte': mascota.updated_at.isoformat(),
                'caracteristicas': mascota.caracteristicas_especiales
            })
        
        return JsonResponse({
            'success': True,
            'total': len(data),
            'mascotas': data
        })
        
    except Exception as e:
        logger.error(f"Error en api_mascotas_perdidas: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)