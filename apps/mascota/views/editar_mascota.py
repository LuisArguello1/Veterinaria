from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.mascota.models import Mascota
from apps.mascota.forms.simple_registro_form import SimpleMascotaRegistroForm


@login_required
def editar_mascota(request, mascota_id):
    """
    Vista para editar información de una mascota existente
    """
    # Verificar que la mascota pertenece al usuario actual
    mascota = get_object_or_404(Mascota, id=mascota_id, propietario=request.user)
    
    if request.method == 'POST':
        form = SimpleMascotaRegistroForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            # Guardar los cambios
            mascota_actualizada = form.save()
            
            # Verificar si es una petición AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'¡{mascota_actualizada.nombre} ha sido actualizada exitosamente!',
                    'mascota_data': {
                        'id': mascota_actualizada.id,
                        'nombre': mascota_actualizada.nombre,
                        'raza': mascota_actualizada.raza or 'No especificada',
                        'edad_completa': mascota_actualizada.edad_completa,
                        'sexo': mascota_actualizada.get_sexo_display() or 'No especificado',
                        'etapa_vida': mascota_actualizada.get_etapa_vida_display() or 'No especificada',
                        'estado_corporal': mascota_actualizada.get_estado_corporal_display() or 'No especificado',
                        'peso': f'{mascota_actualizada.peso} kg' if mascota_actualizada.peso else 'No especificado',
                        'color': mascota_actualizada.color or 'No especificado',
                        'fecha_nacimiento': mascota_actualizada.fecha_nacimiento.strftime('%d/%m/%Y') if mascota_actualizada.fecha_nacimiento else None,
                        'caracteristicas_especiales': mascota_actualizada.caracteristicas_especiales or None,
                        'foto_perfil_url': mascota_actualizada.foto_perfil.url if mascota_actualizada.foto_perfil else None,
                    }
                })
            else:
                messages.success(request, f'¡{mascota_actualizada.nombre} ha sido actualizada exitosamente!')
                return redirect('mascota:main_register')
        else:
            # Si hay errores
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor corrige los errores en el formulario',
                    'errors': errors
                })
            else:
                # Si no es AJAX, mostrar errores normalmente
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    else:
        # GET request - mostrar formulario con datos actuales
        form = SimpleMascotaRegistroForm(instance=mascota)
    
    # Si es una petición AJAX GET (para obtener datos del formulario)
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'mascota_data': {
                'id': mascota.id,
                'nombre': mascota.nombre,
                'raza': mascota.raza or '',
                'sexo': mascota.sexo,
                'edad': mascota.edad,
                'edad_unidad': mascota.edad_unidad,
                'peso': float(mascota.peso) if mascota.peso else '',
                'color': mascota.color or '',
                'estado_corporal': mascota.estado_corporal,
                'etapa_vida': mascota.etapa_vida,
                'fecha_nacimiento': mascota.fecha_nacimiento.strftime('%Y-%m-%d') if mascota.fecha_nacimiento else '',
                'caracteristicas_especiales': mascota.caracteristicas_especiales or '',
                'foto_perfil_url': mascota.foto_perfil.url if mascota.foto_perfil else None,
            }
        })
    
    # Renderizar template normal para peticiones no AJAX
    context = {
        'form': form,
        'mascota': mascota,
        'editing': True
    }
    
    return render(request, 'mascota_registro/form.html', context)