# apps/mascota/views/qr_views.py
import qrcode
from io import BytesIO
import base64
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ..models import Mascota


def mascota_info_publica(request, mascota_uuid):
    """
    Vista pública para mostrar información de la mascota mediante QR
    No requiere autenticación para permitir acceso desde cualquier dispositivo
    """
    try:
        # Buscar mascota por UUID (más seguro que por ID)
        mascota = get_object_or_404(Mascota, uuid=mascota_uuid)
        
        context = {
            'mascota': mascota,
            'propietario': mascota.propietario,
            'es_vista_publica': True,
            'titulo': f'Información de {mascota.nombre}'
        }
        
        return render(request, 'qr/info_publica.html', context)
        
    except Exception as e:
        context = {
            'error': 'Mascota no encontrada o código QR inválido',
            'es_vista_publica': True
        }
        return render(request, 'qr/info_publica.html', context, status=404)


@login_required
def generar_qr_mascota(request, mascota_id):
    """
    Genera el código QR para una mascota específica
    Solo el propietario puede generar el QR de su mascota
    """
    try:
        mascota = get_object_or_404(Mascota, id=mascota_id, propietario=request.user)
        
        # URL pública para la información de la mascota
        url_publica = request.build_absolute_uri(
            reverse('mascota:qr_info_publica', kwargs={'mascota_uuid': str(mascota.uuid)})
        )
        
        # Generar código QR
        qr = qrcode.QRCode(
            version=1,  # Controla el tamaño del QR
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección de errores
            box_size=10,  # Tamaño de cada "caja" del QR
            border=4,  # Grosor del borde
        )
        
        qr.add_data(url_publica)
        qr.make(fit=True)
        
        # Crear imagen del QR
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64 para mostrar en HTML
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': True,
                'qr_image': f'data:image/png;base64,{qr_base64}',
                'url_publica': url_publica,
                'mascota_nombre': mascota.nombre
            })
        
        # Si no es AJAX, redirigir al detalle con el QR
        context = {
            'mascota': mascota,
            'qr_image': f'data:image/png;base64,{qr_base64}',
            'url_publica': url_publica
        }
        
        return render(request, 'mascota/qr/generar_qr.html', context)
        
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': f'Error al generar código QR: {str(e)}'
            }, status=400)
        
        return render(request, 'mascota/qr/generar_qr.html', {
            'error': f'Error al generar código QR: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def descargar_qr_mascota(request, mascota_id):
    """
    Permite descargar el código QR como archivo PNG
    """
    try:
        mascota = get_object_or_404(Mascota, id=mascota_id, propietario=request.user)
        
        # URL pública para la información de la mascota
        url_publica = request.build_absolute_uri(
            reverse('mascota:qr_info_publica', kwargs={'mascota_uuid': str(mascota.uuid)})
        )
        
        # Generar código QR con mayor calidad para descarga
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Mayor corrección de errores
            box_size=15,  # Mayor tamaño para mejor calidad
            border=4,
        )
        
        qr.add_data(url_publica)
        qr.make(fit=True)
        
        # Crear imagen del QR
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Preparar respuesta para descarga
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="QR_{mascota.nombre}_{mascota.id}.png"'
        
        qr_image.save(response, format='PNG')
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al descargar código QR: {str(e)}'
        }, status=400)