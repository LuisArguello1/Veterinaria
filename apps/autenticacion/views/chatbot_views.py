"""
Vistas para la integración con el chatbot de Chatbase
"""
import os
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging
import traceback
import json
from decimal import Decimal
from apps.autenticacion.models import User
from apps.mascota.models import Mascota
# Configurar logger para depuración
logger = logging.getLogger(__name__)

@login_required
def get_chatbot_token(request):
    """
    Genera un token JWT para identificar al usuario en el chatbot de Chatbase
    """
    try:
        # Obtener la clave secreta desde las variables de entorno
        secret = os.environ.get('CHATBOT_IDENTITY_SECRET', 'wa4s2dgvk0in0253mdpiahti7rr3gvve')
        
        if not secret:
            logger.error("Clave secreta no configurada en variables de entorno")
            return JsonResponse({
                'success': False,
                'error': 'Clave secreta no configurada'
            }, status=500)
            
        # Obtener el usuario actual
        user = request.user
        
        # Crear payload del token con información completa del usuario
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'nombre_completo': f"{user.first_name} {user.last_name}".strip() or user.username,
            'rol': user.role if hasattr(user, 'role') else 'OWNER',
            'is_admin': user.is_admin if hasattr(user, 'is_admin') else user.is_superuser,
            'is_owner': getattr(user, 'is_owner', True),
            'is_vet': getattr(user, 'is_vet', False),
            'exp': datetime.utcnow() + timedelta(hours=1)  # Token válido por 1 hora
        }
        
        # Si hay información de contacto, incluirla
        if hasattr(user, 'phone') and user.phone:
            payload['telefono'] = user.phone
        if hasattr(user, 'direction') and user.direction:
            payload['direccion'] = user.direction
            
        # Si el usuario tiene mascotas, incluir información detallada
        try:
            # Registrar para depuración
            logger.debug(f"Intentando obtener mascotas para el usuario {user.username}")
            
            # Verificar si el atributo mascotas existe
            if hasattr(user, 'mascotas'):
                mascotas = user.mascotas.all()
                
                # Registrar la cantidad de mascotas encontradas
                logger.debug(f"Mascotas encontradas: {mascotas.count()}")
                
                if mascotas.exists():
                    payload['mascotas'] = []
                    payload['tiene_mascotas'] = True
                    payload['cantidad_mascotas'] = mascotas.count()
                    
                    for mascota in mascotas[:5]:  # Limitar a 5 mascotas para no sobrecargar el token
                        try:
                            # Datos básicos obligatorios que deberían existir
                            mascota_data = {
                                'id': str(mascota.id),
                                'nombre': str(mascota.nombre),
                            }
                            
                            # Datos adicionales con validación para evitar errores
                            if hasattr(mascota, 'uuid') and mascota.uuid:
                                mascota_data['uuid'] = str(mascota.uuid)
                                
                            if hasattr(mascota, 'raza'):
                                mascota_data['raza'] = mascota.raza or 'No especificada'
                                
                            if hasattr(mascota, 'color'):
                                mascota_data['color'] = mascota.color or 'No especificado'
                                
                            if hasattr(mascota, 'sexo'):
                                mascota_data['sexo'] = mascota.sexo or 'No especificado'
                                if hasattr(mascota, 'get_sexo_display'):
                                    mascota_data['sexo_display'] = mascota.get_sexo_display()
                                    
                            if hasattr(mascota, 'edad'):
                                mascota_data['edad'] = mascota.edad
                                
                            if hasattr(mascota, 'edad_unidad'):
                                mascota_data['edad_unidad'] = mascota.edad_unidad
                                if hasattr(mascota, 'get_edad_unidad_display'):
                                    mascota_data['edad_unidad_display'] = mascota.get_edad_unidad_display()
                                
                            if hasattr(mascota, 'etapa_vida'):
                                mascota_data['etapa_vida'] = mascota.etapa_vida or 'No especificada'
                                if hasattr(mascota, 'get_etapa_vida_display'):
                                    mascota_data['etapa_vida_display'] = mascota.get_etapa_vida_display()
                                
                            if hasattr(mascota, 'estado_corporal'):
                                mascota_data['estado_corporal'] = mascota.estado_corporal or 'Normal'
                                if hasattr(mascota, 'get_estado_corporal_display'):
                                    mascota_data['estado_corporal_display'] = mascota.get_estado_corporal_display()
                                
                            if hasattr(mascota, 'biometria_entrenada'):
                                mascota_data['biometria_entrenada'] = mascota.biometria_entrenada
                                
                            if hasattr(mascota, 'reportar_perdida'):
                                mascota_data['reportar_perdida'] = mascota.reportar_perdida
                            
                            # Intentar obtener el conteo de imágenes biométricas
                            if hasattr(mascota, 'get_biometric_image_count'):
                                try:
                                    mascota_data['total_imagenes_biometricas'] = mascota.get_biometric_image_count()
                                except Exception as e:
                                    logger.error(f"Error al obtener conteo de imágenes biométricas: {str(e)}")
                            
                            # Incluir URL de foto si existe
                            if hasattr(mascota, 'foto_perfil') and mascota.foto_perfil:
                                try:
                                    mascota_data['foto_url'] = request.build_absolute_uri(mascota.foto_perfil.url)
                                except Exception as e:
                                    logger.error(f"Error al obtener URL de la foto: {str(e)}")
                            
                            # Añadir datos de recomendaciones si el método existe
                            if hasattr(mascota, 'get_recomendaciones_cuidado'):
                                try:
                                    mascota_data['recomendaciones'] = mascota.get_recomendaciones_cuidado()
                                except Exception as e:
                                    logger.error(f"Error al obtener recomendaciones: {str(e)}")
                            
                            # Añadir peso si existe
                            if hasattr(mascota, 'peso') and mascota.peso:
                                mascota_data['peso'] = mascota.peso
                                
                            # Añadir características especiales si existen
                            if hasattr(mascota, 'caracteristicas_especiales') and mascota.caracteristicas_especiales:
                                mascota_data['caracteristicas_especiales'] = mascota.caracteristicas_especiales
                            
                            # Agregar la mascota al payload
                            payload['mascotas'].append(mascota_data)
                            
                        except Exception as e:
                            logger.error(f"Error procesando mascota {mascota.id}: {str(e)}")
                else:
                    payload['tiene_mascotas'] = False
                    payload['cantidad_mascotas'] = 0
                
                # Incluir información sobre mascotas perdidas
                mascotas_perdidas = mascotas.filter(reportar_perdida=True)
                payload['tiene_mascotas_perdidas'] = mascotas_perdidas.exists()
                
                if mascotas_perdidas.exists():
                    payload['mascotas_perdidas'] = [
                        {
                            'id': str(mascota.id),
                            'nombre': mascota.nombre,
                            'uuid': str(mascota.uuid) if mascota.uuid else None,
                        }
                        for mascota in mascotas_perdidas[:3]
                    ]
                
        except:
            # Si hay algún error al acceder a las mascotas, continúa sin incluirlas
            pass
        
        # Convertir decimales a flotantes para la serialización JSON
        def decimal_converter(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        # Convertir todo el payload a tipos serializables
        def convert_payload(obj):
            if isinstance(obj, dict):
                return {k: convert_payload(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_payload(item) for item in obj]
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return obj
        
        # Convertir todo el payload para asegurar que no haya objetos Decimal
        payload = convert_payload(payload)
        
        # Generar token JWT
        token = jwt.encode(payload, secret, algorithm='HS256')
        
        return JsonResponse({
            'success': True,
            'token': token
        })
        
    except Exception as e:
        # Registrar el error detallado para depuración
        logger.error(f"Error generando token para chatbot: {str(e)}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=500)