# apps/mascota/views/registro_view.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from apps.mascota.forms.registro_form import MascotaRegistroForm
from apps.mascota.services.ai_predictor import predictor
from apps.mascota.models import Mascota


@login_required
def registro_mascota_view(request):
    """Vista principal para el registro de mascotas"""
    
    # Verificar el número actual de mascotas del usuario
    maximo_mascota = Mascota.objects.filter(propietario=request.user).count()
    
    # Verificar si ya alcanzó el límite máximo (2 mascotas)
    if maximo_mascota >= 2:
        messages.error(request, 'Has alcanzado el límite máximo de 2 mascotas por usuario. No puedes registrar más mascotas.')
        return redirect('mascota:main_register')
    
    if request.method == 'POST':
        # Verificar nuevamente en POST por seguridad
        if maximo_mascota >= 2:
            messages.error(request, 'Has alcanzado el límite máximo de 2 mascotas por usuario.')
            return redirect('mascota:main_register')
            
        form = MascotaRegistroForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Obtener predicciones de IA si hay foto
            predictions = form.get_ai_predictions()
            
            # Aplicar predicciones si el usuario las acepta
            if predictions:
                form.apply_ai_predictions(predictions)
            
            # Guardar la mascota
            mascota = form.save(commit=False)
            mascota.propietario = request.user
            mascota.save()
            
            messages.success(request, f'¡{mascota.nombre} ha sido registrada exitosamente!')
            return redirect('mascota:main_register')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = MascotaRegistroForm()

    context = {
        'form': form,
        'title': 'Registrar Nueva Mascota',
        'maximo_mascotas': maximo_mascota
    }
    
    return render(request, 'mascota_registro/form.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def predict_from_image_ajax(request):
    """
    Vista AJAX para obtener predicciones de IA desde una imagen
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó imagen'
            })
        
        image_file = request.FILES['image']
        
        # Validar que es una imagen
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({
                'success': False,
                'error': 'El archivo debe ser una imagen'
            })
        
        # Validar tamaño (máximo 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'La imagen no puede ser mayor a 5MB'
            })
        
        # Obtener predicciones
        result = predictor.predict_from_image_file(image_file)
        
        if result['success']:
            predictions = result['predictions']
            
            # Formatear respuesta para el frontend
            response_data = {
                'success': True,
                'predictions': {
                    'breed': {
                        'predicted': predictions['breed']['predicted'],
                        'confidence': round(predictions['breed']['confidence'], 3),
                        'confidence_percentage': round(predictions['breed']['confidence'] * 100, 1),
                        'confidence_level': predictions['breed']['confidence_level'],
                        'display_name': _get_breed_display_name(predictions['breed']['predicted']),
                        'all_probabilities': {
                            k: {
                                'probability': round(v, 3),
                                'percentage': round(v * 100, 1),
                                'display_name': _get_breed_display_name(k)
                            }
                            for k, v in predictions['breed']['all_probabilities'].items()
                        }
                    },
                    'stage': {
                        'predicted': predictions['stage']['predicted'],
                        'confidence': round(predictions['stage']['confidence'], 3),
                        'confidence_percentage': round(predictions['stage']['confidence'] * 100, 1),
                        'confidence_level': predictions['stage']['confidence_level'],
                        'display_name': predictions['stage']['predicted'].capitalize(),
                        'all_probabilities': {
                            k: {
                                'probability': round(v, 3),
                                'percentage': round(v * 100, 1),
                                'display_name': k.capitalize()
                            }
                            for k, v in predictions['stage']['all_probabilities'].items()
                        }
                    }
                }
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Error desconocido en predicción')
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error procesando solicitud: {str(e)}'
        })


def _get_breed_display_name(breed_internal):
    """Convierte el nombre interno de la raza a un nombre para mostrar"""
    breed_mapping = {
        'bulldog': 'Bulldog',
        'chihuahua': 'Chihuahua',
        'golden retriever': 'Golden Retriever'
    }
    return breed_mapping.get(breed_internal, breed_internal.title())


@require_http_methods(["GET"])
def check_ai_model_status(request):
    """Vista para verificar el estado del modelo de IA"""
    try:
        # Verificar si el modelo está cargado
        model_available = predictor.model is not None
        
        return JsonResponse({
            'success': True,
            'model_available': model_available,
            'message': 'Modelo disponible' if model_available else 'Modelo no disponible'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })