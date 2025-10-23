from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.mascota.models import Mascota
from apps.mascota.forms import MascotaCreateForm
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, FormView, ListView, TemplateView


@login_required
def main_register(request):
    # Obtenemos todas las mascotas del usuario
    try:
        # Primero hacemos todas las operaciones ORM sin slice
        mascotas_queryset = Mascota.objects.filter(propietario=request.user).order_by('-created_at')
        
        # Verificar si se debe activar automáticamente la pestaña de biometría
        biometria_id = request.GET.get('biometria_id')
        
        # Crear una instancia del formulario de registro
        form = MascotaCreateForm()
        
        # Si el usuario tiene al menos una mascota, las pasamos al template
        if mascotas_queryset.exists():
            # Importamos el modelo de imágenes
            from apps.mascota.models import ImagenMascota
            
            # Aplicamos el límite de 2 mascotas al final
            mascotas = mascotas_queryset[:2]
            
            # Verificar si todas las mascotas ya tienen biometría entrenada
            # Usamos el queryset original para hacer el conteo correcto
            mascotas_con_biometria = mascotas_queryset.filter(biometria_entrenada=True).count()
            total_mascotas = mascotas_queryset.count()
            todas_mascotas_entrenadas = mascotas_con_biometria == total_mascotas and total_mascotas > 0
            
            # Preparamos el contexto con la lista de mascotas (limitada a 2)
            context = {
                'mascotas': mascotas,
                'mascota_count': len(mascotas),  # len() porque mascotas ya es una lista después del slice
                'active_biometria_id': biometria_id,  # Para activar automáticamente la pestaña
                'mascotas_con_biometria': mascotas_con_biometria,
                'todas_mascotas_entrenadas': todas_mascotas_entrenadas,
                'form': form  # Agregamos el formulario al contexto
            }
            
            # Para cada mascota, preparamos los datos adicionales
            mascota_data = []
            for mascota in mascotas:
                # Agrupamos imágenes por tipo para esta mascota
                images_by_type = {}
                for tipo, label in ImagenMascota.TIPO_CHOICES:
                    images = mascota.imagenes.filter(tipo=tipo)
                    if images.exists():
                        images_by_type[label] = images
                
                # Datos de esta mascota
                data = {
                    'id': mascota.id,
                    'mascota': mascota,
                    'total_images': mascota.imagenes.count(),
                    'biometric_images': mascota.imagenes.filter(tipo='biometrica').count(),
                    'biometria_entrenada': mascota.biometria_entrenada,
                    'tiene_suficientes_imagenes': mascota.tiene_suficientes_imagenes,
                    'images_by_type': images_by_type
                }
                mascota_data.append(data)
                
            context['mascota_data'] = mascota_data
            
            return render(request, 'main_register.html', context)
        else:
            # Si no tiene mascotas, mostramos un mensaje y seguimos sin mascota en el contexto
            messages.info(request, "No tiene mascotas registradas. Por favor, registre una nueva mascota.")
            return render(request, 'main_register.html', {
                'mascota_count': 0,
                'form': form  # Agregamos el formulario al contexto
            })
            
    except Exception as e:
        messages.error(request, f"Error al cargar los datos de la mascota: {str(e)}")
        return render(request, 'main_register.html', {
            'mascota_count': 0,
            'form': form  # Agregamos el formulario al contexto
        })



