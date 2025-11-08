"""
Vistas para el mapa interactivo de mascotas perdidas y encontradas
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db.models import Q
import logging

from ..models import Mascota

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def mapa_mascotas(request):
    """
    Renderiza la página del mapa interactivo de mascotas perdidas/encontradas
    """
    try:
        # Obtener el token de Mapbox desde settings
        mapbox_token = getattr(settings, 'MAPBOX_TOKEN', '')
        
        # Log para diagnóstico
        if not mapbox_token:
            logger.warning("⚠️ MAPBOX_TOKEN no está configurado en settings")
        else:
            logger.info(f"✅ MAPBOX_TOKEN configurado (longitud: {len(mapbox_token)})")
            # Verificar que comienza con 'pk.'
            if not mapbox_token.startswith('pk.'):
                logger.warning(f"⚠️ El token de Mapbox no parece válido (debe comenzar con 'pk.')")
        
        context = {
            'mapbox_token': mapbox_token,
            'page_title': 'Mapa de Mascotas Perdidas',
        }
        
        return render(request, 'mascota/mapa/mapa_mascotas.html', context)
        
    except Exception as e:
        logger.error(f"Error cargando mapa de mascotas: {str(e)}")
        return render(request, 'mascota/mapa/mapa_mascotas.html', {
            'error': 'Error al cargar el mapa',
            'mapbox_token': ''
        })


@require_http_methods(["GET"])
def api_mascotas_mapa(request):
    """
    API que devuelve:
    - Todas las mascotas perdidas (de todos los usuarios) - PIN ROJO
    - Reportes de mascotas encontradas (solo de las mascotas del usuario actual) - PIN NARANJA
    """
    try:
        from ..models import ReporteMascotaEncontrada
        
        # Obtener filtro opcional
        filtro = request.GET.get('filtro', 'todas')
        
        logger.info(f"🗺️ API Mapa - Solicitando datos con filtro: {filtro}, usuario: {request.user}")
        
        datos_mapa = []
        
        # SIEMPRE mostrar todas las mascotas perdidas (de cualquier usuario)
        if filtro in ['perdidas', 'todas']:
            mascotas_perdidas = Mascota.objects.filter(
                reportar_perdida=True,
                latitud__isnull=False,
                longitud__isnull=False
            ).select_related('propietario')
            
            logger.info(f"   📍 Mascotas perdidas: {mascotas_perdidas.count()}")
            
            for mascota in mascotas_perdidas:
                logger.info(f"      - {mascota.nombre} (ID: {mascota.id}): PERDIDA")
                
                # Obtener URL de la foto (absoluta)
                foto_url = None
                if mascota.foto_perfil:
                    foto_url = request.build_absolute_uri(mascota.foto_perfil.url)
                else:
                    # Buscar primera imagen de la mascota
                    primera_imagen = mascota.imagenes.first()
                    if primera_imagen and primera_imagen.imagen:
                        foto_url = request.build_absolute_uri(primera_imagen.imagen.url)
                
                datos_mapa.append({
                    'id': mascota.id,
                    'tipo': 'perdida',
                    'nombre': mascota.nombre,
                    'raza': mascota.raza or 'Sin raza',
                    'foto': foto_url,
                    'latitud': float(mascota.latitud),
                    'longitud': float(mascota.longitud),
                    'ubicacion_descripcion': mascota.ubicacion_descripcion or 'Ubicación donde se perdió',
                    'fecha_reporte': mascota.fecha_ubicacion.isoformat() if mascota.fecha_ubicacion else None,
                    'propietario': {
                        'nombre': mascota.propietario.get_full_name() or mascota.propietario.username,
                        'telefono': getattr(mascota.propietario, 'telefono', None),
                    },
                    'caracteristicas': mascota.caracteristicas_especiales,
                    'uuid': str(mascota.uuid),
                    'estado': 'perdida'
                })
        
        # Mostrar reportes de encontrada SOLO de las mascotas del usuario autenticado
        if filtro in ['reportes', 'todas'] and request.user.is_authenticated:
            reportes = ReporteMascotaEncontrada.objects.filter(
                mascota__propietario=request.user,
                estado='pendiente',
                latitud__isnull=False,
                longitud__isnull=False
            ).select_related('mascota', 'reportado_por')
            
            logger.info(f"   📍 Reportes de encontrada del usuario: {reportes.count()}")
            
            for reporte in reportes:
                logger.info(f"      - Reporte ID {reporte.id}: {reporte.mascota.nombre} encontrada")
                
                # Foto del reporte (la imagen escaneada) o foto de perfil de la mascota
                foto_url = None
                if reporte.foto_reporte:
                    foto_url = request.build_absolute_uri(reporte.foto_reporte.url)
                    logger.info(f"   📸 Usando foto del reporte: {foto_url}")
                elif reporte.mascota.foto_perfil:
                    foto_url = request.build_absolute_uri(reporte.mascota.foto_perfil.url)
                    logger.info(f"   📸 Usando foto de perfil de la mascota: {foto_url}")
                else:
                    # Buscar primera imagen de la mascota
                    primera_imagen = reporte.mascota.imagenes.first()
                    if primera_imagen and primera_imagen.imagen:
                        foto_url = request.build_absolute_uri(primera_imagen.imagen.url)
                        logger.info(f"   📸 Usando primera imagen biométrica: {foto_url}")
                
                reportante = 'Anónimo'
                if reporte.reportado_por:
                    reportante = reporte.reportado_por.get_full_name() or reporte.reportado_por.username
                elif reporte.nombre_reportante:
                    reportante = reporte.nombre_reportante
                
                datos_mapa.append({
                    'id': f"reporte_{reporte.id}",
                    'tipo': 'reporte_encontrada',
                    'reporte_id': reporte.id,
                    'mascota_id': reporte.mascota.id,
                    'nombre': reporte.mascota.nombre,
                    'raza': reporte.mascota.raza or 'Sin raza',
                    'foto': foto_url,
                    'latitud': float(reporte.latitud),
                    'longitud': float(reporte.longitud),
                    'ubicacion_descripcion': reporte.ubicacion_descripcion or 'Ubicación donde fue encontrada',
                    'fecha_reporte': reporte.fecha_reporte.isoformat(),
                    'reportante': reportante,
                    'reportante_telefono': reporte.telefono_reportante,
                    'reportante_email': reporte.email_reportante,
                    'caracteristicas': reporte.mascota.caracteristicas_especiales,
                    'uuid': str(reporte.mascota.uuid),
                    'estado': 'reporte_encontrada',
                    'es_mi_mascota': True  # Siempre es del usuario actual
                })
        
        return JsonResponse({
            'success': True,
            'count': len(datos_mapa),
            'mascotas': datos_mapa
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos para el mapa: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error al obtener datos de mascotas'
        }, status=500)





@require_http_methods(["GET"])
def api_mascota_detalle_mapa(request, mascota_id):
    """
    API que devuelve los detalles completos de una mascota específica para mostrar en el popup
    """
    try:
        mascota = Mascota.objects.select_related('propietario').get(id=mascota_id)
        
        # Determinar el estado
        estado = 'perdida' if mascota.reportar_perdida else 'encontrada'
        
        # URL de la foto
        foto_url = None
        if mascota.foto_perfil:
            foto_url = mascota.foto_perfil.url
        else:
            primera_imagen = mascota.imagenes.first()
            if primera_imagen:
                foto_url = primera_imagen.imagen.url
        
        # Construir datos detallados
        datos = {
            'id': mascota.id,
            'uuid': str(mascota.uuid),
            'nombre': mascota.nombre,
            'raza': mascota.raza or 'No especificada',
            'estado': estado,
            'latitud': float(mascota.latitud) if mascota.latitud else None,
            'longitud': float(mascota.longitud) if mascota.longitud else None,
            'ubicacion_descripcion': mascota.ubicacion_descripcion or 'Ubicación no especificada',
            'fecha_ubicacion': mascota.fecha_ubicacion.isoformat() if mascota.fecha_ubicacion else None,
            'foto_url': foto_url,
            'propietario': {
                'nombre': mascota.propietario.get_full_name() or mascota.propietario.username,
                'telefono': mascota.propietario.phone if hasattr(mascota.propietario, 'phone') else None,
                'email': mascota.propietario.email if not mascota.reportar_perdida else None
            },
            'caracteristicas': mascota.caracteristicas_especiales or 'Sin características especiales',
            'sexo': mascota.get_sexo_display() if mascota.sexo else 'No especificado',
            'edad': mascota.edad_completa,
            'color': mascota.color or 'No especificado',
            'peso': float(mascota.peso) if mascota.peso else None,
            'estado_corporal': mascota.get_estado_corporal_display() if mascota.estado_corporal else None,
        }
        
        return JsonResponse({
            'success': True,
            'mascota': datos
        })
        
    except Mascota.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mascota no encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f"Error obteniendo detalle de mascota {mascota_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error al obtener detalles de la mascota'
        }, status=500)
