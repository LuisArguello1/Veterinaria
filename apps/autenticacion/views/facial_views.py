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
import json
import base64
import logging

from apps.autenticacion.models import User, UserFaceEmbedding
from apps.autenticacion.utils.facial_recognition import facial_system

logger = logging.getLogger(__name__)


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
class DetectFaceView(View):
    """Vista para detectar rostros en tiempo real"""
    
    def post(self, request, *args, **kwargs):
        """Recibe un frame y retorna si se detectó un rostro"""
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({
                    'success': False,
                    'message': 'No se recibió imagen'
                }, status=400)
            
            # Decodificar imagen base64
            image_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Detectar rostro
            image, faces, confidence = facial_system.detect_faces(image_bytes)
            
            if not faces:
                return JsonResponse({
                    'success': False,
                    'face_detected': False,
                    'message': 'No se detectó ningún rostro'
                })
            
            face_info = faces[0]
            
            return JsonResponse({
                'success': True,
                'face_detected': True,
                'confidence': confidence,
                'bbox': face_info['bbox'],
                'message': 'Rostro detectado correctamente'
            })
            
        except Exception as e:
            logger.error(f"Error en detección de rostro: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar imagen: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterFacialBiometryView(LoginRequiredMixin, View):
    """Vista para registrar la biometría facial del usuario"""
    
    def post(self, request, *args, **kwargs):
        """Registra el descriptor facial del usuario"""
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({
                    'success': False,
                    'message': 'No se recibió imagen'
                }, status=400)
            
            # Decodificar imagen
            image_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Extraer descriptor facial
            descriptor_data = facial_system.extract_face_descriptor(image_bytes)
            
            if not descriptor_data:
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudo extraer el descriptor facial. Asegúrate de que tu rostro esté bien iluminado y centrado.'
                })
            
            # Verificar que la confianza sea suficiente
            if descriptor_data['confidence'] < facial_system.CONFIDENCE_THRESHOLD:
                return JsonResponse({
                    'success': False,
                    'message': f'La calidad del rostro es baja ({descriptor_data["confidence"]:.2f}). Por favor, intenta con mejor iluminación.'
                })
            
            # Serializar descriptor
            descriptor_json = facial_system.serialize_descriptor(descriptor_data)
            
            # Guardar o actualizar en la base de datos
            face_embedding, created = UserFaceEmbedding.objects.update_or_create(
                user=request.user,
                defaults={
                    'descriptor_data': descriptor_json,
                    'confidence_score': descriptor_data['confidence'],
                    'face_bbox': descriptor_data['bbox'],
                    'is_active': True,
                    'allow_login': True,
                }
            )
            
            action = "registrada" if created else "actualizada"
            
            return JsonResponse({
                'success': True,
                'message': f'Biometría facial {action} exitosamente',
                'confidence': descriptor_data['confidence'],
                'created': created
            })
            
        except Exception as e:
            logger.error(f"Error al registrar biometría: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar biometría: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyFacialLoginView(View):
    """Vista para verificar el login mediante reconocimiento facial"""
    
    def post(self, request, *args, **kwargs):
        """Verifica el rostro y autentica al usuario"""
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({
                    'success': False,
                    'message': 'No se recibió imagen'
                }, status=400)
            
            # Decodificar imagen
            image_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Extraer descriptor del rostro capturado
            captured_descriptor = facial_system.extract_face_descriptor(image_bytes)
            
            if not captured_descriptor:
                return JsonResponse({
                    'success': False,
                    'message': 'No se detectó ningún rostro. Por favor, intenta nuevamente.'
                })
            
            # Buscar coincidencia en la base de datos
            best_match = None
            best_similarity = 0.0
            
            # Obtener todos los usuarios con biometría activa
            active_embeddings = UserFaceEmbedding.objects.filter(
                is_active=True,
                allow_login=True
            ).select_related('user')
            
            for embedding in active_embeddings:
                try:
                    # Deserializar descriptor almacenado
                    stored_descriptor = facial_system.deserialize_descriptor(
                        embedding.descriptor_data
                    )
                    
                    # Comparar rostros
                    similarity, is_match = facial_system.compare_faces(
                        captured_descriptor['descriptor'],
                        stored_descriptor['descriptor']
                    )
                    
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
                
                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido {user.get_full_name()}!',
                    'similarity': best_similarity,
                    'redirect_url': str(reverse_lazy('auth:Dashboard'))
                })
            else:
                # No se encontró coincidencia
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
@method_decorator(csrf_exempt, name='dispatch')
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
class ToggleFacialLoginView(LoginRequiredMixin, View):
    """Vista para activar/desactivar el login facial"""
    
    def post(self, request, *args, **kwargs):
        """Activa o desactiva el login facial"""
        try:
            data = json.loads(request.body)
            allow_login = data.get('allow_login', True)
            
            logger.info(f"Usuario {request.user.username} solicitó cambiar estado de login a: {allow_login}")
            
            # Buscar biometría activa
            try:
                face_embedding = UserFaceEmbedding.objects.get(
                    user=request.user,
                    is_active=True
                )
            except UserFaceEmbedding.DoesNotExist:
                logger.warning(f"Usuario {request.user.username} intentó cambiar estado sin biometría activa")
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes biometría facial activa'
                }, status=404)
            
            face_embedding.allow_login = allow_login
            face_embedding.save()
            
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


# Importar timezone para timestamps
from django.utils import timezone
