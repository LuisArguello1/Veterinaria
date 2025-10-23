# apps/mascota/views/carnet.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse_lazy
from apps.mascota.models import Mascota
import os
from io import BytesIO
import base64

# Importaciones para PDF (opcional)
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

@login_required
def lista_carnets(request):
    """
    Vista para mostrar todos los carnets de las mascotas del usuario
    """
    mascotas = Mascota.objects.filter(propietario=request.user).select_related('propietario')
    
    context = {
        'mascotas': mascotas,
        'title': 'Carnets de Mascotas',
        'pdf_available': PDF_AVAILABLE
    }

    context['breadcrumb_list'] = [
        {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
        {'label': 'Carnets'}
    ]
    
    return render(request, 'carnet/lista_carnets.html', context)

@login_required
def detalle_carnet(request, mascota_id):
    """
    Vista para mostrar el carnet detallado de una mascota específica
    """
    mascota = get_object_or_404(
        Mascota.objects.select_related('propietario'), 
        id=mascota_id, 
        propietario=request.user
    )
    
    context = {
        'mascota': mascota,
        'propietario': mascota.propietario,
        'title': f'Carnet de {mascota.nombre}',
        'pdf_available': PDF_AVAILABLE
    }

    context['breadcrumb_list'] = [
        {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
        {'label': 'Carnets', 'url': reverse_lazy('mascota:lista_carnets')},
        {'label': 'Detalle carnet'}
    ]
    
    return render(request, 'carnet/detalle_carnet.html', context)

@login_required
def descargar_carnet_pdf(request, mascota_id):
    """
    Vista para descargar el carnet en formato PDF
    """
    if not PDF_AVAILABLE:
        raise Http404("La generación de PDF no está disponible")
    
    mascota = get_object_or_404(
        Mascota.objects.select_related('propietario'), 
        id=mascota_id, 
        propietario=request.user
    )
    
    # Crear el PDF en memoria
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.darkgreen
    )
    
    # Título principal
    title = Paragraph("CARNET DE IDENTIFICACIÓN", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Subtítulo con nombre de mascota
    subtitle = Paragraph(f"Mascota: {mascota.nombre}", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Crear tabla con información
    data = [
        ['INFORMACIÓN DE LA MASCOTA', ''],
        ['Nombre:', mascota.nombre or 'No especificado'],
        ['Raza:', mascota.raza or 'No especificada'],
        ['Sexo:', mascota.sexo_display],
        ['Edad:', mascota.edad_completa],
        ['Peso:', f"{mascota.peso} kg" if mascota.peso else 'No especificado'],
        ['Color:', mascota.color or 'No especificado'],
        ['Estado Corporal:', mascota.get_estado_corporal_display() if mascota.estado_corporal else 'No especificado'],
        ['Etapa de Vida:', mascota.etapa_vida_display],
        ['Fecha de Nacimiento:', mascota.fecha_nacimiento.strftime('%d/%m/%Y') if mascota.fecha_nacimiento else 'No especificada'],
        ['UUID:', str(mascota.uuid) if mascota.uuid else 'No asignado'],
        ['', ''],
        ['INFORMACIÓN DEL PROPIETARIO', ''],
        ['Nombre Completo:', f"{mascota.propietario.first_name} {mascota.propietario.last_name}"],
        ['Usuario:', mascota.propietario.username],
        ['Email:', mascota.propietario.email],
        ['Teléfono:', mascota.propietario.phone or 'No especificado'],
        ['Dirección:', mascota.propietario.direction or 'No especificada'],
        ['Cédula:', mascota.propietario.dni or 'No especificada'],
    ]
    
    # Agregar características especiales si existen
    if mascota.caracteristicas_especiales:
        data.extend([
            ['', ''],
            ['CARACTERÍSTICAS ESPECIALES', ''],
            ['Descripción:', mascota.caracteristicas_especiales]
        ])
    
    # Crear la tabla
    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        # Estilo para encabezados
        ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 12), (1, 12), colors.darkgreen),
        ('TEXTCOLOR', (0, 12), (1, 12), colors.whitesmoke),
        
        # Estilo general
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Estilo para las etiquetas (primera columna)
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Nota al pie
    footer = Paragraph(
        f"Carnet generado el {mascota.created_at.strftime('%d/%m/%Y')} | Sistema PetFaceID",
        styles['Normal']
    )
    elements.append(footer)
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el contenido del buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta HTTP
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="carnet_{mascota.nombre}_{mascota.id}.pdf"'
    
    return response

@login_required
def vista_previa_carnet(request, mascota_id):
    """
    Vista previa del carnet en HTML para impresión
    """
    mascota = get_object_or_404(
        Mascota.objects.select_related('propietario'), 
        id=mascota_id, 
        propietario=request.user
    )
    
    context = {
        'mascota': mascota,
        'propietario': mascota.propietario,
        'title': f'Vista Previa - Carnet de {mascota.nombre}',
        'is_preview': True
    }

    context['breadcrumb_list'] = [
        {'label': 'Dashboard', 'url': reverse_lazy('auth:Dashboard')},
        {'label': 'Carnets', 'url': reverse_lazy('mascota:lista_carnets')},
        {'label': 'Detalle carnet', 'url': reverse_lazy('mascota:detalle_carnet')},
        {'label': 'Vista previa'},
    ]
    
    return render(request, 'carnet/vista_previa_carnet.html', context)
