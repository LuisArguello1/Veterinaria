from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.mascota.models import Mascota

@login_required
def get_user_pets(request):
    """
    Endpoint para obtener las mascotas del usuario actual en formato JSON.
    Esta función es usada por el selector de mascotas en el frontend.
    """
    try:
        # Obtener las mascotas del usuario actual (máximo 2)
        mascotas_queryset = Mascota.objects.filter(propietario=request.user).order_by('-created_at')
        mascotas = mascotas_queryset[:2]  # Aplicar el slice al final
        
        # Formatear los datos para la respuesta JSON
        mascotas_data = []
        for mascota in mascotas:
            # Obtener la URL de la primera imagen si existe
            imagen_url = None
            if mascota.imagenes.exists():
                imagen_url = mascota.imagenes.first().imagen.url
                
            # Datos básicos de la mascota
            mascotas_data.append({
                'id': mascota.id,
                'nombre': mascota.nombre,
                'raza': mascota.raza or 'No especificada',
                'edad': mascota.edad_completa,
                'imagen_url': imagen_url,
                'biometria_entrenada': mascota.biometria_entrenada
            })
        
        return JsonResponse({
            'success': True,
            'mascotas': mascotas_data,
            'total': len(mascotas_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)