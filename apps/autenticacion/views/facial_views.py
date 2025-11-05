"""
Vistas para el sistema de reconocimiento facial
Maneja el registro y verificación de biometría facial de usuarios
"""
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from zoneinfo import ZoneInfo
import json
import base64
import logging

from apps.autenticacion.models import User, UserFaceEmbedding, Notification
from apps.autenticacion.utils.facial_recognition import arcface_system
from apps.autenticacion.utils.notifications_helper import notify_success, notify_warning

logger = logging.getLogger(__name__)

# Configuración de seguridad
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB máximo por imagen


def validate_image_data(image_data):
    """
    Valida los datos de la imagen antes de procesarla
    Returns: (image_bytes, error_message)
    """
    if not image_data:
        return None, 'No se recibió imagen'
    
    try:
        # Decodificar imagen base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        
        # Validar tamaño
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return None, f'La imagen es demasiado grande (máximo {MAX_IMAGE_SIZE // 1024 // 1024}MB)'
        
        return image_bytes, None
        
    except Exception as e:
        logger.error(f"Error al decodificar imagen: {e}")
        return None, 'Formato de imagen inválido'


class FacialBiometryRegisterView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar la interfaz de registro de biometría facial"""
    template_name = 'autenticacion/profile/facial_register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Biometría Facial'
        
        # Verificar si el usuario ya tiene biometría registrada
        try:
            face_embedding = self.request.user.face_embedding
            context['has_biometry'] = True
            context['biometry_info'] = {
                'created_at': face_embedding.created_at,
                'confidence': face_embedding.confidence_score,
                'successful_logins': face_embedding.successful_logins,
                'is_active': face_embedding.is_active,
                'allow_login': face_embedding.allow_login,
            }
        except UserFaceEmbedding.DoesNotExist:
            context['has_biometry'] = False
        
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
            {'label': 'Mi perfil', 'url': reverse_lazy('auth:profile')},
            {'label': 'Biometría Facial'}
        ]
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='30/m', method='POST'), name='dispatch')
class DetectFaceView(View):
    """Vista para detectar rostros en tiempo real"""
    
    def post(self, request, *args, **kwargs):
        """Recibe un frame y retorna si se detectó un rostro"""
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            # Validar imagen
            image_bytes, error = validate_image_data(image_data)
            
            if error:
                return JsonResponse({
                    'success': False,
                    'message': error
                }, status=400)
            
            # Detectar rostro con validación de único rostro
            image, face_info, error = arcface_system.detect_and_validate_single_face(image_bytes)
            
            if error:
                # Determinar tipo de error
                error_type = 'no_face'
                if 'detectaron' in error.lower():
                    error_type = 'multiple_faces'
                
                return JsonResponse({
                    'success': False,
                    'face_detected': False,
                    'message': error,
                    'error_type': error_type
                })
            
            return JsonResponse({
                'success': True,
                'face_detected': True,
                'confidence': face_info['confidence'],
                'bbox': face_info['bbox'],
                'landmarks': face_info['landmarks'],
                'message': 'Rostro detectado correctamente'
            })
            
        except Exception as e:
            logger.error(f"Error en detección de rostro: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar imagen: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='user', rate='10/h', method='POST'), name='dispatch')
class RegisterFacialBiometryView(LoginRequiredMixin, View):
    """Vista para registrar la biometría facial del usuario"""
    
    def post(self, request, *args, **kwargs):
        """Registra el embedding facial del usuario con ArcFace"""
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            # Validar imagen
            image_bytes, error = validate_image_data(image_data)
            
            if error:
                return JsonResponse({
                    'success': False,
                    'message': error
                }, status=400)
            
            # Extraer embedding con ArcFace
            embedding_data, error = arcface_system.extract_face_embedding(image_bytes)
            
            if error:
                # Determinar tipo de error para mejor UX
                error_type = 'processing_error'
                if 'detectaron' in error.lower():
                    error_type = 'multiple_faces'
                elif 'no se detectó' in error.lower():
                    error_type = 'no_face'
                
                return JsonResponse({
                    'success': False,
                    'message': error,
                    'error_type': error_type
                })
            
            # Verificar confianza mínima
            if embedding_data['confidence'] < arcface_system.CONFIDENCE_THRESHOLD:
                return JsonResponse({
                    'success': False,
                    'message': f'Calidad del rostro baja ({embedding_data["confidence"]:.1%}). Por favor, mejora la iluminación e intenta nuevamente.'
                })
            
            # Guardar o actualizar en la base de datos
            face_embedding, created = UserFaceEmbedding.objects.update_or_create(
                user=request.user,
                defaults={
                    'embedding_vector': embedding_data['embedding'],
                    'embedding_size': embedding_data['embedding_size'],
                    'confidence_score': embedding_data['confidence'],
                    'face_bbox': embedding_data['bbox'],
                    'model_version': embedding_data['model_version'],
                    'is_active': True,
                    'allow_login': True,
                }
            )
            
            action = "registrada" if created else "actualizada"
            
            # Crear notificación de registro/actualización de biometría facial
            notify_success(
                user=request.user,
                title=f"¡Biometría facial {action}!",
                message=f"Tu reconocimiento facial ha sido {action} exitosamente con una confianza del {embedding_data['confidence']*100:.1f}%. Ya puedes iniciar sesión con tu rostro.",
                category=Notification.NotificationCategory.BIOMETRIA
            )
            
            logger.info(f"Biometría {action} para usuario {request.user.username} - Confianza: {embedding_data['confidence']:.2%}")
            
            return JsonResponse({
                'success': True,
                'message': f'Biometría facial {action} exitosamente',
                'confidence': embedding_data['confidence'],
                'embedding_size': embedding_data['embedding_size'],
                'created': created
            })
            
        except Exception as e:
            logger.error(f"Error al registrar biometría para {request.user.username}: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar biometría: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='10/m', method='POST'), name='dispatch')
class VerifyFacialLoginView(View):
    """Vista para verificar el login mediante reconocimiento facial con ArcFace"""
    
    def post(self, request, *args, **kwargs):
        """Verifica el rostro y autentica al usuario"""
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            # Validar imagen
            image_bytes, error = validate_image_data(image_data)
            
            if error:
                return JsonResponse({
                    'success': False,
                    'message': error
                }, status=400)
            
            # Extraer embedding del rostro capturado con ArcFace
            captured_embedding, error = arcface_system.extract_face_embedding(image_bytes)
            
            if error:
                return JsonResponse({
                    'success': False,
                    'message': error
                })
            
            # Buscar coincidencia en la base de datos
            best_match = None
            best_similarity = 0.0
            
            # Obtener todos los usuarios con biometría activa
            active_embeddings = UserFaceEmbedding.objects.filter(
                is_active=True,
                allow_login=True
            ).select_related('user')
            
            logger.info(f"Comparando con {active_embeddings.count()} usuarios activos...")
            
            for embedding in active_embeddings:
                try:
                    # Comparar embeddings de ArcFace
                    similarity, is_match = arcface_system.compare_embeddings(
                        captured_embedding['embedding'],
                        embedding.embedding_vector
                    )
                    
                    logger.debug(f"Usuario {embedding.user.username}: similitud={similarity:.3f}, match={is_match}")
                    
                    if is_match and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = embedding
                        
                except Exception as e:
                    logger.error(f"Error al comparar con usuario {embedding.user.username}: {e}")
                    continue
            
            if best_match:
                # Autenticar al usuario
                user = best_match.user
                
                # Verificar que el usuario esté activo
                if not user.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tu cuenta está desactivada.'
                    })
                
                # Actualizar estadísticas
                best_match.successful_logins += 1
                best_match.last_successful_login = timezone.now()
                best_match.failed_attempts = 0
                best_match.save()
                
                # Iniciar sesión
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Crear notificación de inicio de sesión facial con hora de Ecuador (prevenir duplicados)
                from datetime import timedelta
                
                hora_ecuador = timezone.now().astimezone(ZoneInfo('America/Guayaquil'))
                
                # Verificar si ya existe una notificación de login facial reciente (últimos 10 segundos)
                recent_facial_login = Notification.objects.filter(
                    user=user,
                    title="¡Inicio de sesión facial exitoso!",
                    category=Notification.NotificationCategory.SYSTEM,
                    created_at__gte=timezone.now() - timedelta(seconds=10)
                ).exists()
                
                # Solo crear la notificación si no hay una reciente
                if not recent_facial_login:
                    notify_success(
                        user=user,
                        title="¡Inicio de sesión facial exitoso!",
                        message=f"Has iniciado sesión mediante reconocimiento facial el {hora_ecuador.strftime('%d/%m/%Y a las %H:%M')} con una confianza del {best_similarity*100:.1f}%.",
                        category=Notification.NotificationCategory.SYSTEM
                    )
                
                logger.info(f"✓ Login facial exitoso: {user.username} (similitud: {best_similarity:.3f})")
                
                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido {user.get_full_name() or user.username}!',
                    'similarity': best_similarity,
                    'redirect_url': str(reverse_lazy('auth:Dashboard'))
                })
            else:
                # No se encontró coincidencia
                logger.warning(f"✗ No se reconoció ningún rostro (mejor similitud: {best_similarity:.3f})")
                return JsonResponse({
                    'success': False,
                    'message': 'No se reconoció tu rostro. Por favor, intenta nuevamente o usa tu contraseña.'
                })
                
        except Exception as e:
            logger.error(f"Error en verificación facial: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al verificar rostro: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='user', rate='5/h', method='POST'), name='dispatch')
class DeleteFacialBiometryView(LoginRequiredMixin, View):
    """Vista para eliminar la biometría facial del usuario"""
    
    def post(self, request, *args, **kwargs):
        """Elimina o desactiva la biometría facial"""
        try:
            logger.info(f"Usuario {request.user.username} solicitó eliminar biometría")
            
            # Buscar biometría activa
            try:
                face_embedding = UserFaceEmbedding.objects.get(
                    user=request.user,
                    is_active=True
                )
            except UserFaceEmbedding.DoesNotExist:
                logger.warning(f"Usuario {request.user.username} intentó eliminar biometría inexistente o ya eliminada")
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes biometría facial activa para eliminar'
                }, status=404)
            
            # Desactivar en lugar de eliminar (para mantener historial)
            face_embedding.is_active = False
            face_embedding.allow_login = False
            face_embedding.save()
            
            # Crear notificación de eliminación de biometría facial
            notify_warning(
                user=request.user,
                title="Biometría facial eliminada",
                message="Tu reconocimiento facial ha sido desactivado. Ya no podrás iniciar sesión con tu rostro hasta que lo registres nuevamente.",
                category=Notification.NotificationCategory.BIOMETRIA
            )
            
            logger.info(f"Biometría eliminada exitosamente para usuario {request.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Biometría facial eliminada correctamente'
            })
            
        except Exception as e:
            logger.error(f"Error al eliminar biometría para usuario {request.user.username}: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar biometría: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='user', rate='20/h', method='POST'), name='dispatch')
class ToggleFacialLoginView(LoginRequiredMixin, View):
    """Vista para activar/desactivar el login facial"""
    
    def post(self, request, *args, **kwargs):
        """Activa o desactiva el login facial"""
        try:
            data = json.loads(request.body)
            allow_login = data.get('allow_login', True)
            
            logger.info(f"Usuario {request.user.username} solicitó cambiar estado de login a: {allow_login}")
            
            # Buscar biometría (activa o no, solo que exista)
            try:
                face_embedding = UserFaceEmbedding.objects.get(
                    user=request.user
                )
                
                # Verificar que esté activa (no eliminada)
                if not face_embedding.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'No tienes biometría facial registrada. Regístrala primero.'
                    }, status=404)
                    
            except UserFaceEmbedding.DoesNotExist:
                logger.warning(f"Usuario {request.user.username} intentó cambiar estado sin biometría")
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes biometría facial registrada'
                }, status=404)
            
            # Actualizar el estado de allow_login
            face_embedding.allow_login = allow_login
            face_embedding.save(update_fields=['allow_login'])
            
            status = "activado" if allow_login else "desactivado"
            
            logger.info(f"Login facial {status} para usuario {request.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': f'Login facial {status} correctamente',
                'allow_login': allow_login
            })
            
        except Exception as e:
            logger.error(f"Error al cambiar estado de login facial para usuario {request.user.username}: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
