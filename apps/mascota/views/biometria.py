"""
Vistas para la gestión de la biometría de mascotas.
Incluye subida de imágenes, entrenamiento de modelo y reconocimiento.
También incluye vistas para la gestión de mascotas como el detalle y listado.
"""

import base64
import json
import os
import uuid
from datetime import datetime
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import View, DetailView, FormView, ListView, TemplateView
from django.db.models import Count

from ..models import Mascota, ImagenMascota, ModeloGlobal, EmbeddingStore, RegistroReconocimiento
from ..services.biometria import (
    procesar_imagen_mascota, 
    actualizar_modelo_global,
    reconocer_mascota,
    BiometriaService, 
    DEPS_INSTALLED
)


@login_required
@require_GET
def get_user_pets(request):
    """
    Vista que devuelve las mascotas del usuario actual en formato JSON.
    Útil para el selector de mascotas en la interfaz de datos biométricos.
    """
    try:
        # Obtener mascotas del usuario actual
        mascotas = Mascota.objects.filter(propietario=request.user)
        
        # Preparar datos para JSON
        mascotas_data = []
        for mascota in mascotas:
            # Obtener información básica de cada mascota
            mascota_data = {
                'id': mascota.id,
                'nombre': mascota.nombre,
                'raza': mascota.raza or 'No especificada',
                'especie': 'Canino',  # Asumimos que son perros por defecto
                'imagenes_count': ImagenMascota.objects.filter(mascota=mascota).count()
            }
            mascotas_data.append(mascota_data)
        
        return JsonResponse({
            'success': True,
            'mascotas': mascotas_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@method_decorator(login_required, name='dispatch')
class BiometriaView(DetailView):
    """Vista para la página de biometría de una mascota."""
    model = Mascota
    template_name = 'biometria_registro/biometria.html'
    context_object_name = 'mascota'
    
    def get_object(self, queryset=None):
        """
        Obtiene el objeto mascota. Si se proporciona pk en la URL, lo usa;
        si no, intenta obtenerlo desde el parámetro id en la query string.
        """
        if self.kwargs.get('pk'):
            # Si hay un pk en la URL, usamos el comportamiento predeterminado
            return super().get_object(queryset)
        
        # Si no hay pk en la URL, buscamos un parámetro id en la query string
        mascota_id = self.request.GET.get('id')
        if not mascota_id:
            return None  # Esto provocará un error 404
        
        # Filtrar por el id de la query y por el propietario
        queryset = self.get_queryset()
        queryset = queryset.filter(id=mascota_id, propietario=self.request.user)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            return None
            
        return obj
    
    def get(self, request, *args, **kwargs):
        """
        Maneja la petición GET. Si no hay mascota (ni por pk ni por id), 
        redirige a la página principal de registro de mascotas.
        Para peticiones AJAX, devuelve solo el template de biometría.
        """
        try:
            self.object = self.get_object()
            if not self.object:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': 'Mascota no encontrada o no tienes permiso para acceder.'
                    }, status=404)
                messages.warning(request, "Mascota no encontrada o no tienes permiso para acceder.")
                return redirect('mascota:main_register')
            
            context = self.get_context_data(object=self.object)
            
            # Si es una petición AJAX, devolver solo el template de biometría
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'biometria_registro/biometria.html', context)
            
            # Si no es AJAX, redirigir a la página principal con el ID en la URL
            # para mantener la funcionalidad de pestañas
            return redirect(f"{reverse('mascota:main_register')}?biometria_id={self.object.id}")
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Error al acceder a la mascota especificada.'
                }, status=500)
            messages.warning(request, "No se pudo acceder a la mascota especificada.")
            return redirect('mascota:main_register')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deps_installed'] = DEPS_INSTALLED
        if not DEPS_INSTALLED:
            messages.warning(self.request, 
                "Las dependencias para biometría no están instaladas. Por favor, instala PyTorch, OpenCV y scikit-learn.")
        return context


@login_required
@require_POST
def upload_biometria_image(request):
    """Vista para subir imágenes biométricas de mascotas."""
    mascota_id = request.POST.get('mascota_id')
    if not mascota_id:
        return JsonResponse({'success': False, 'error': 'ID de mascota no proporcionado'}, status=400)
        
    try:
        mascota = Mascota.objects.get(id=mascota_id)
        
        # Verificar que la mascota pertenece al usuario
        if mascota.propietario != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para subir imágenes a esta mascota'}, status=403)
            
        files = request.FILES.getlist('imagenes')
        if not files:
            return JsonResponse({'success': False, 'error': 'No se proporcionaron archivos'}, status=400)
            
        # Verificar límite de imágenes actual
        current_images = mascota.imagenes.filter(is_biometrica=True).count()
        
        # Validar que no se excedan las 20 imágenes total
        if len(files) > 20:
            return JsonResponse({
                'success': False, 
                'error': 'Solo puedes subir un máximo de 20 imágenes por vez.'
            }, status=400)
            
        # Validar que no se exceda el límite total considerando las imágenes existentes
        if current_images + len(files) > 20:
            remaining = 20 - current_images
            return JsonResponse({
                'success': False, 
                'error': f'Solo puedes subir {remaining} imágenes más. Ya tienes {current_images}/20 imágenes.',
                'images_count': current_images,
                'images_remaining': remaining
            }, status=400)
            
        # Subir imágenes de forma optimizada
        count = 0
        imagenes_creadas = []
        
        for file in files:
            # Verificar límite durante el proceso
            current_count = mascota.imagenes.filter(is_biometrica=True).count()
            if current_count >= 20:
                break  # Ya se alcanzó el límite, detener
                
            # Verificar que sea una imagen
            if not file.content_type.startswith('image/'):
                continue
                
            # Crear objeto ImagenMascota (sin procesar aún)
            imagen = ImagenMascota.objects.create(
                mascota=mascota,
                imagen=file,
                tipo='biometrica',
                is_biometrica=True
            )
            
            imagenes_creadas.append(imagen.id)
            count += 1
            
        # Procesar todas las imágenes en un hilo separado para no bloquear la respuesta
        if imagenes_creadas:
            import threading
            def procesar_imagenes_background():
                for imagen_id in imagenes_creadas:
                    try:
                        procesar_imagen_mascota(imagen_id)
                    except Exception as e:
                        print(f"Error al procesar imagen {imagen_id}: {e}")
            
            # Ejecutar en segundo plano
            threading.Thread(target=procesar_imagenes_background, daemon=True).start()
            
        # Obtener conteo final
        final_count = mascota.imagenes.filter(is_biometrica=True).count()
            
        return JsonResponse({
            'success': True, 
            'count': count, 
            'message': f'{count} imágenes subidas correctamente',
            'images_count': final_count,
            'images_remaining': max(0, 20 - final_count),
            'limit_reached': final_count >= 20
        })
        
    except Mascota.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mascota no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def upload_biometria_base64(request):
    """Vista para subir una imagen biométrica en formato base64 (desde la cámara)."""
    mascota_id = request.POST.get('mascota_id')
    imagen_base64 = request.POST.get('imagen_base64')
    tipo = request.POST.get('tipo', 'biometrica')
    
    if not mascota_id or not imagen_base64:
        return JsonResponse({'success': False, 'error': 'Faltan datos requeridos'}, status=400)
        
    try:
        mascota = Mascota.objects.get(id=mascota_id)
        
        # Verificar que la mascota pertenece al usuario
        if mascota.propietario != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para subir imágenes a esta mascota'}, status=403)
            
        # Verificar límite de 20 imágenes biométricas
        current_images = mascota.imagenes.filter(is_biometrica=True).count()
        if current_images >= 20:
            return JsonResponse({
                'success': False, 
                'error': 'Límite alcanzado: ya tienes 20 imágenes biométricas para esta mascota.',
                'images_count': current_images,
                'limit_reached': True
            }, status=400)
            
        # Procesar base64
        if ',' in imagen_base64:
            _, imagen_base64 = imagen_base64.split(',', 1)
            
        # Decodificar base64
        imagen_data = base64.b64decode(imagen_base64)
        
        # Crear nombre de archivo único
        filename = f"{uuid.uuid4().hex}.jpg"
        
        # Crear objeto ImagenMascota
        imagen = ImagenMascota(
            mascota=mascota,
            tipo=tipo,
            is_biometrica=True
        )
        
        # Guardar imagen
        imagen.imagen.save(filename, ContentFile(imagen_data))
        imagen.save()
        
        # Procesar imagen en segundo plano
        try:
            procesar_imagen_mascota(imagen.id)
        except Exception as e:
            print(f"Error al procesar imagen: {e}")
        
        # Obtener conteo actualizado
        new_images_count = mascota.imagenes.filter(is_biometrica=True).count()
        
        return JsonResponse({
            'success': True, 
            'message': 'Imagen subida correctamente',
            'imagen_id': imagen.id,
            'images_count': new_images_count,
            'images_remaining': max(0, 20 - new_images_count),
            'limit_reached': new_images_count >= 20
        })
        
    except Mascota.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mascota no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def delete_imagen(request, pk):
    """Vista para eliminar una imagen biométrica."""
    try:
        imagen = ImagenMascota.objects.get(id=pk)
        
        # Verificar que la imagen pertenece al usuario
        if imagen.mascota.propietario != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para eliminar esta imagen'}, status=403)
            
        # Eliminar imagen
        imagen.delete()
        
        return JsonResponse({'success': True, 'message': 'Imagen eliminada correctamente'})
        
    except ImagenMascota.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Imagen no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_GET
def get_mascota_stats(request, pk):
    """Vista para obtener estadísticas de una mascota."""
    try:
        mascota = Mascota.objects.get(id=pk)
        
        # Verificar que la mascota pertenece al usuario
        if mascota.propietario != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para ver esta mascota'}, status=403)
            
        # Obtener datos
        images_count = mascota.imagenes.filter(is_biometrica=True).count()
        biometria_entrenada = mascota.biometria_entrenada
        confianza = mascota.confianza_biometrica
        
        return JsonResponse({
            'success': True,
            'images_count': images_count,
            'biometria_entrenada': biometria_entrenada,
            'confianza': confianza,
            'reload_gallery': False
        })
        
    except Mascota.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mascota no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def train_model(request, pk):
    """Vista para entrenar el modelo biométrico de una mascota."""
    try:
        mascota = Mascota.objects.get(id=pk)
        
        # Verificar que la mascota pertenece al usuario
        if mascota.propietario != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para entrenar esta mascota'}, status=403)
            
        # Verificar que hay suficientes imágenes
        images_count = mascota.imagenes.filter(is_biometrica=True).count()
        if images_count < 20:
            return JsonResponse({
                'success': False, 
                'error': f'Se necesitan al menos 20 imágenes para entrenar (tienes {images_count})'
            }, status=400)
            
        # Verificar que hay embeddings disponibles
        embeddings_count = EmbeddingStore.objects.filter(mascota=mascota).count()
        if embeddings_count < 5:
            # Procesar todas las imágenes sin procesar
            imagenes_sin_procesar = mascota.imagenes.filter(is_biometrica=True, procesada=False)
            for img in imagenes_sin_procesar:
                try:
                    procesar_imagen_mascota(img.id)
                except Exception as e:
                    print(f"Error al procesar imagen {img.id}: {e}")
            
            # Verificar nuevamente
            embeddings_count = EmbeddingStore.objects.filter(mascota=mascota).count()
            if embeddings_count < 5:
                return JsonResponse({
                    'success': False, 
                    'error': 'No hay suficientes características extraídas para entrenar'
                }, status=400)
        
        # Entrenar modelo
        try:
            start_time = time.time()
            modelo = actualizar_modelo_global(tipo_modelo='knn', extractor='efficientnet_b0', n_neighbors=5)
            end_time = time.time()
            
            if modelo:
                # Actualizar estado de la mascota
                mascota.biometria_entrenada = True
                mascota.confianza_biometrica = modelo.metricas.get('accuracy', 0.0) if modelo.metricas else 0.8
                mascota.save()
                
                return JsonResponse({
                    'success': True,
                    'modelo_id': modelo.id,
                    'tiempo': round(end_time - start_time, 2),
                    'message': 'Modelo entrenado correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo entrenar el modelo. Verifica que haya suficientes imágenes procesadas.'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al entrenar modelo: {str(e)}'}, status=500)
            
    except Mascota.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mascota no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
class MascotaDetailView(DetailView):
    """Vista para mostrar el detalle de una mascota específica."""
    model = Mascota
    template_name = 'mi_mascota/detail.html'
    context_object_name = 'mascota'
    
    def get_queryset(self):
        """Filtrar solo las mascotas del usuario autenticado."""
        return Mascota.objects.filter(propietario=self.request.user)
    
        
    def get(self, request, *args, **kwargs):
        """
        Maneja la petición GET con depuración adicional.
        """
        try:
            # Obtener el ID de la mascota de la URL
            pk = kwargs.get('pk')
            
            # Depuración: verificar si la mascota existe en absoluto
            mascota_exists = Mascota.objects.filter(id=pk).exists()
            
            # Depuración: verificar si el usuario tiene mascotas
            user_mascotas = Mascota.objects.filter(propietario=request.user)
            
            # Mostrar mensajes de depuración
            if not mascota_exists:
                messages.error(request, f"La mascota con ID {pk} no existe en la base de datos.")
            elif not user_mascotas.filter(id=pk).exists():
                owner = Mascota.objects.get(id=pk).propietario
                messages.error(request, f"La mascota con ID {pk} existe pero pertenece a otro usuario: {owner.username}")
                messages.info(request, f"Tu usuario es: {request.user.username}")
            
            if not user_mascotas.exists():
                messages.warning(request, "No tienes ninguna mascota registrada.")
                messages.info(request, f"Total de mascotas en el sistema: {Mascota.objects.count()}")
                
            # Continuar con el comportamiento normal de DetailView
            return super().get(request, *args, **kwargs)
        except Mascota.DoesNotExist:
            messages.error(request, "La mascota solicitada no existe.")
            return redirect('mascota:main_register')
        except Exception as e:
            messages.error(request, f"Error al acceder al detalle: {str(e)}")
            return redirect('mascota:main_register')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota = self.get_object()
        
        # Solo incluimos un mensaje informativo conciso
        messages.info(self.request, f"Visualizando detalles de {mascota.nombre}")
        
        # Agrupar imágenes por tipo
        images_by_type = {}
        for tipo, label in ImagenMascota.TIPO_CHOICES:
            images = mascota.imagenes.filter(tipo=tipo)
            if images.exists():
                images_by_type[label] = images
                
        # Información general para el contexto
        context['images_by_type'] = images_by_type
        context['total_images'] = mascota.imagenes.count()
        context['biometric_images'] = mascota.imagenes.filter(tipo='biometrica').count()
        
        # Información sobre el entrenamiento biométrico
        context['biometria_entrenada'] = mascota.biometria_entrenada
        context['tiene_suficientes_imagenes'] = mascota.tiene_suficientes_imagenes
        
        # Historial de reconocimientos
        context['reconocimientos'] = RegistroReconocimiento.objects.filter(
            mascota_predicha=mascota
        ).order_by('-fecha')[:5]  # Últimos 5 reconocimientos
        
        return context


@method_decorator(login_required, name='dispatch')
class ScannerView(View):
    """Vista para el escáner de mascotas."""
    template_name = 'scanner/scanner.html'
    
    def get(self, request):
        context = {
            'deps_installed': DEPS_INSTALLED
        }
        
        if not DEPS_INSTALLED:
            messages.warning(request, 
                "Las dependencias para biometría no están instaladas. Por favor, instala PyTorch, OpenCV y scikit-learn.")
        
        # Verificar que hay mascotas con biometría entrenada
        mascotas_entrenadas = Mascota.objects.filter(
            biometria_entrenada=True
        ).count()
        
        if mascotas_entrenadas == 0:
            messages.warning(request, 
                "No existen mascotas con biometría entrenada. Por favor, registra mascotas, sube imágenes biométricas y entrena el modelo.")
            context['tiene_mascotas_entrenadas'] = False
        else:
            context['tiene_mascotas_entrenadas'] = True
            context['mascotas_entrenadas_count'] = mascotas_entrenadas
                
        # Verificar que hay un modelo activo
        modelo_activo = ModeloGlobal.get_active_model()
        if not modelo_activo:
            messages.warning(request, 
                "No hay un modelo biométrico entrenado. Por favor, entrena el modelo con las imágenes biométricas.")
            context['modelo_activo'] = False
        else:
            context['modelo_activo'] = True
            context['modelo'] = modelo_activo
            
        # El scanner está habilitado solo si hay dependencias, modelo activo y mascotas entrenadas
        context['scanner_habilitado'] = (
            DEPS_INSTALLED and 
            modelo_activo and 
            mascotas_entrenadas > 0
        )
            
        # Obtener últimos reconocimientos (solo de mascotas que aún existen)
        context['ultimos_reconocimientos'] = RegistroReconocimiento.objects.filter(
            usuario=request.user,
            mascota_predicha__isnull=False  # Solo reconocimientos con mascota válida
        ).select_related('mascota_predicha').order_by('-fecha')[:5]
            
        return render(request, self.template_name, context)


@login_required
@require_POST
def upload_image_for_recognition(request):
    """Vista para subir una imagen y reconocer la mascota."""
    if not DEPS_INSTALLED:
        return JsonResponse({'success': False, 'error': 'Dependencias no instaladas'}, status=400)
        
    # Verificar que hay un modelo activo
    modelo_activo = ModeloGlobal.get_active_model()
    if not modelo_activo:
        return JsonResponse({'success': False, 'error': 'No hay un modelo biométrico entrenado'}, status=400)
        
    # Verificar si es una imagen base64 o un archivo
    if request.POST.get('imagen_base64'):
        imagen_base64 = request.POST.get('imagen_base64')
        
        # Procesar base64
        if ',' in imagen_base64:
            _, imagen_base64 = imagen_base64.split(',', 1)
            
        # Decodificar base64
        imagen_data = base64.b64decode(imagen_base64)
        
        # Crear archivo temporal
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Crear nombre de archivo único
        filename = os.path.join(temp_dir, f"{uuid.uuid4().hex}.jpg")
        
        # Guardar imagen temporal
        with open(filename, 'wb') as f:
            f.write(imagen_data)
    else:
        # Procesar archivo subido
        if 'imagen' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No se proporcionó una imagen'}, status=400)
            
        imagen_file = request.FILES['imagen']
        
        # Verificar que sea una imagen
        if not imagen_file.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'El archivo no es una imagen'}, status=400)
            
        # Crear archivo temporal
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Crear nombre de archivo único
        filename = os.path.join(temp_dir, f"{uuid.uuid4().hex}.jpg")
        
        # Guardar imagen temporal
        with open(filename, 'wb') as f:
            for chunk in imagen_file.chunks():
                f.write(chunk)
    
    try:
        # Reconocer mascota
        resultado = reconocer_mascota(filename)
        
        # Si hay un error
        if 'error' in resultado:
            return JsonResponse({'success': False, 'error': resultado['error']}, status=400)
            
        # Obtener mascota reconocida
        if resultado['exito'] and resultado.get('mascota'):
            # Actualizar el registro con el usuario
            registro = RegistroReconocimiento.objects.get(id=resultado['registro_id'])
            registro.usuario = request.user
            registro.save()
            
            # Los datos ya vienen completos desde reconocer_mascota()
            # Verificar si la mascota está reportada como perdida
            mascota_obj = Mascota.objects.get(id=resultado['mascota']['id'])
            
            # Asegurar que el UUID esté incluido en los datos de la mascota
            mascota_data = resultado['mascota'].copy()
            mascota_data['uuid'] = str(mascota_obj.uuid)  # Asegurar que el UUID esté presente
            
            return JsonResponse({
                'success': True,
                'reconocimiento': {
                    'exito': True,
                    'confianza': resultado['confianza'],
                    'tiempo_procesamiento': resultado['tiempo_procesamiento'],
                    'mensaje': resultado.get('mensaje', f'¡Mascota identificada exitosamente! {resultado["mascota"]["nombre"]} (Confianza: {resultado["confianza"]:.1%})')
                },
                'mascota': mascota_data,  # Usar datos actualizados con UUID
                'propietario': resultado.get('propietario'),
                'mascota_perdida': mascota_obj.reportar_perdida  # Agregar información de si está perdida
            })
        else:
            return JsonResponse({
                'success': True,
                'reconocimiento': {
                    'exito': False,
                    'confianza': resultado['confianza'],
                    'tiempo_procesamiento': resultado['tiempo_procesamiento'],
                    'mensaje': resultado.get('mensaje', 'No se pudo identificar la mascota con suficiente confianza')
                }
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    finally:
        # Eliminar archivo temporal
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass
