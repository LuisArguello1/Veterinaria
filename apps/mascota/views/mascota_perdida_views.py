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
from apps.autenticacion.utils.notifications_helper import notify_mascota
from apps.autenticacion.models import Notification

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
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        
        # Log para debugging
        logger.info(f"📍 Reportando perdida - Mascota: {mascota.nombre}")
        logger.info(f"   Ubicación descripción: {ubicacion_perdida}")
        logger.info(f"   Latitud recibida: {latitud}")
        logger.info(f"   Longitud recibida: {longitud}")
        
        # Convertir coordenadas a float si existen
        lat_float = None
        lng_float = None
        
        if latitud and longitud:
            try:
                lat_float = float(latitud)
                lng_float = float(longitud)
                logger.info(f"   ✅ Coordenadas convertidas: ({lat_float}, {lng_float})")
            except (ValueError, TypeError) as e:
                logger.error(f"   ❌ Error convirtiendo coordenadas: {e}")
        else:
            logger.warning(f"   ⚠️ No se recibieron coordenadas")
        
        # Reportar como perdida
        exito, mensaje = MascotaPerdidaService.reportar_como_perdida(
            mascota, request.user, ubicacion_perdida, lat_float, lng_float
        )
        
        # Crear notificación si fue exitoso
        if exito:
            notify_mascota(
                user=request.user,
                title=f"¡{mascota.nombre} ha sido reportada como perdida!",
                message=f"Tu mascota {mascota.nombre} ha sido marcada como perdida. La comunidad será notificada y recibirás alertas si alguien la encuentra.",
                mascota=mascota,
                notification_type=Notification.NotificationType.WARNING
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
        
        # Crear notificación si fue exitoso (mascota encontrada)
        if exito:
            notify_mascota(
                user=request.user,
                title=f"¡{mascota.nombre} ha sido encontrada!",
                message=f"Tu mascota {mascota.nombre} ya no está marcada como perdida. ¡Qué bueno que la encontraste!",
                mascota=mascota,
                notification_type=Notification.NotificationType.SUCCESS
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
        from ..models import RegistroReconocimiento, ReporteMascotaEncontrada
        from ..services.email_service import EmailService
        from apps.autenticacion.utils.notifications_helper import notify_mascota
        from apps.autenticacion.models import Notification
        
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
        usuario_reportante = request.user if request.user.is_authenticated else None
        
        # Obtener foto del reporte si existe en FILES
        foto_reporte = request.FILES.get('foto_reporte')
        
        # Si no hay foto en FILES, buscar el último reconocimiento exitoso de esta mascota
        if not foto_reporte:
            logger.info(f"🔍 No se proporcionó foto, buscando último reconocimiento de {mascota.nombre}")
            ultimo_reconocimiento = RegistroReconocimiento.objects.filter(
                mascota_predicha=mascota,
                exito=True,
                imagen_analizada__isnull=False
            ).order_by('-fecha').first()
            
            if ultimo_reconocimiento and ultimo_reconocimiento.imagen_analizada:
                logger.info(f"✅ Encontrado reconocimiento ID {ultimo_reconocimiento.id} con imagen")
                # Usar directamente el archivo del reconocimiento
                foto_reporte = ultimo_reconocimiento.imagen_analizada
            else:
                logger.warning(f"⚠️ No se encontró reconocimiento reciente con imagen para {mascota.nombre}")
        
        # Obtener datos de ubicación directamente del POST
        lat = request.POST.get('latitud')
        lng = request.POST.get('longitud')
        descripcion = request.POST.get('ubicacion_encontrada', '')
        
        logger.info("="*80)
        logger.info(f"🔍 INICIO DEBUG REPORTE ENCONTRADA")
        logger.info(f"🔍 POST keys disponibles: {list(request.POST.keys())}")
        logger.info(f"🔍 POST data completo: {dict(request.POST)}")
        logger.info(f"🔍 FILES keys: {list(request.FILES.keys())}")
        logger.info(f"🔍 lat recibido: '{lat}' (tipo: {type(lat).__name__})")
        logger.info(f"🔍 lng recibido: '{lng}' (tipo: {type(lng).__name__})")
        logger.info(f"🔍 descripcion recibida: '{descripcion}' (tipo: {type(descripcion).__name__})")
        logger.info(f"🔍 lat is None: {lat is None}, lat bool: {bool(lat)}")
        logger.info(f"🔍 lng is None: {lng is None}, lng bool: {bool(lng)}")
        logger.info("="*80)
        
        # CREAR EL REPORTE DIRECTAMENTE AQUÍ
        try:
            logger.info("🔄 Creando instancia de ReporteMascotaEncontrada...")
            # Crear el reporte con los datos que tenemos
            reporte = ReporteMascotaEncontrada(
                mascota=mascota,
                ip_address=ip_address,
                user_agent=user_agent,
                reportado_por=usuario_reportante,
                estado='pendiente'
            )
            logger.info(f"✅ Instancia creada. ID antes de save: {reporte.id}")
            
            # Asignar coordenadas si existen
            logger.info(f"🔍 Evaluando if lat and lng: lat={bool(lat)}, lng={bool(lng)}")
            if lat and lng:
                logger.info("✅ Entrando al bloque de coordenadas...")
                try:
                    lat_float = float(lat)
                    lng_float = float(lng)
                    logger.info(f"✅ Conversión exitosa: lat_float={lat_float}, lng_float={lng_float}")
                    
                    reporte.latitud = lat_float
                    reporte.longitud = lng_float
                    logger.info(f"✅ Coordenadas asignadas al objeto reporte")
                    logger.info(f"   reporte.latitud = {reporte.latitud}")
                    logger.info(f"   reporte.longitud = {reporte.longitud}")
                except ValueError as e:
                    logger.error(f"❌ Error convirtiendo coordenadas: {e}")
            else:
                logger.warning(f"⚠️ NO se asignaron coordenadas. lat={lat}, lng={lng}")
            
            # Asignar descripción de ubicación
            if descripcion:
                reporte.ubicacion_descripcion = descripcion
                logger.info(f"✅ Descripción asignada: {descripcion}")
            else:
                logger.warning(f"⚠️ NO se asignó descripción (vacía o None)")
            
            # Asignar foto si existe
            if foto_reporte:
                reporte.foto_reporte = foto_reporte
                logger.info(f"✅ Foto asignada: {foto_reporte}")
            else:
                logger.warning(f"⚠️ NO se asignó foto")
            
            # VERIFICAR VALORES ANTES DE GUARDAR
            logger.info("="*80)
            logger.info("🔍 VALORES ANTES DE SAVE():")
            logger.info(f"   mascota: {reporte.mascota}")
            logger.info(f"   latitud: {reporte.latitud} (tipo: {type(reporte.latitud).__name__})")
            logger.info(f"   longitud: {reporte.longitud} (tipo: {type(reporte.longitud).__name__})")
            logger.info(f"   ubicacion_descripcion: {reporte.ubicacion_descripcion}")
            logger.info(f"   foto_reporte: {reporte.foto_reporte}")
            logger.info(f"   estado: {reporte.estado}")
            logger.info("="*80)
            
            # GUARDAR EL REPORTE
            logger.info("💾 Llamando a reporte.save()...")
            reporte.save()
            logger.info(f"✅✅✅ REPORTE GUARDADO EXITOSAMENTE - ID: {reporte.id}")
            
            # Verificar que se guardó correctamente
            reporte.refresh_from_db()
            logger.info(f"🔍 VERIFICACIÓN POST-GUARDADO:")
            logger.info(f"   - ID: {reporte.id}")
            logger.info(f"   - Latitud: {reporte.latitud}")
            logger.info(f"   - Longitud: {reporte.longitud}")
            logger.info(f"   - Ubicación: {reporte.ubicacion_descripcion}")
            logger.info(f"   - Foto: {reporte.foto_reporte}")
            
            # Ahora enviar notificaciones
            ubicacion_data = None
            if lat and lng:
                ubicacion_data = {
                    'lat': float(lat),
                    'lng': float(lng),
                    'descripcion': descripcion
                }
            
            # Enviar notificaciones (email y app)
            # Notificación in-app
            ubicacion_texto = ""
            if lat and lng:
                ubicacion_texto = f" cerca de las coordenadas {lat}, {lng}"
            
            notify_mascota(
                user=mascota.propietario,
                title=f"¡Alguien encontró a {mascota.nombre}!",
                message=f"¡Buenas noticias! Alguien ha reportado haber encontrado a {mascota.nombre}{ubicacion_texto}. Revisa los reportes para confirmar.",
                mascota=mascota,
                notification_type=Notification.NotificationType.SUCCESS
            )
            
            # Email al propietario
            datos_encuentro = MascotaPerdidaService._obtener_datos_encuentro(ip_address, user_agent, ubicacion_data)
            datos_encuentro['reporte_id'] = reporte.id
            EmailService.enviar_notificacion_mascota_encontrada(mascota, datos_encuentro)
            
            exito = True
            mensaje = f"¡Reporte de {mascota.nombre} registrado exitosamente! El propietario ha sido notificado."
            reporte_id = reporte.id
            
        except Exception as e:
            logger.error(f"❌❌❌ ERROR CREANDO REPORTE: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            exito = False
            mensaje = f"Error al crear el reporte: {str(e)}"
            reporte_id = None
        
        return JsonResponse({
            'success': exito,
            'message' if exito else 'error': mensaje,
            'reporte_id': reporte_id,
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


@login_required
@require_http_methods(["POST"])
def confirmar_reporte_encontrada(request, reporte_id):
    """
    Confirma que un reporte de mascota encontrada es correcto
    Solo el propietario de la mascota puede confirmar
    """
    try:
        from ..models import ReporteMascotaEncontrada
        
        reporte = get_object_or_404(ReporteMascotaEncontrada, id=reporte_id)
        
        # Verificar que el usuario es el propietario de la mascota
        if reporte.mascota.propietario != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para confirmar este reporte'
            }, status=403)
        
        # Confirmar el reporte (pasando el propietario como argumento)
        reporte.confirmar(propietario=request.user)
        
        # La mascota ya se marca como encontrada dentro del método confirmar()
        mascota = reporte.mascota
        
        # Crear notificación de éxito
        notify_mascota(
            user=request.user,
            title=f"¡{mascota.nombre} ha sido encontrada!",
            message=f"Has confirmado que {mascota.nombre} fue encontrada. ¡Qué alegría que estén juntos de nuevo! El reporte ha sido marcado como confirmado.",
            mascota=mascota,
            notification_type=Notification.NotificationType.SUCCESS
        )
        
        logger.info(f"✅ Reporte {reporte_id} confirmado por {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'¡Excelente! {mascota.nombre} ha sido marcada como encontrada.'
        })
        
    except Exception as e:
        logger.error(f"Error confirmando reporte {reporte_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error al confirmar el reporte'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def descartar_reporte_encontrada(request, reporte_id):
    """
    Descarta un reporte de mascota encontrada
    Solo el propietario de la mascota puede descartar
    """
    try:
        from ..models import ReporteMascotaEncontrada
        
        reporte = get_object_or_404(ReporteMascotaEncontrada, id=reporte_id)
        
        # Verificar que el usuario es el propietario de la mascota
        if reporte.mascota.propietario != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para descartar este reporte'
            }, status=403)
        
        # Guardar info para el log antes de eliminar
        mascota_nombre = reporte.mascota.nombre
        
        # Eliminar el reporte completamente
        reporte.delete()
        
        logger.info(f"🗑️ Reporte {reporte_id} de {mascota_nombre} eliminado por {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'El reporte ha sido eliminado.'
        })
        
    except Exception as e:
        logger.error(f"Error descartando reporte {reporte_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error al descartar el reporte'
        }, status=500)