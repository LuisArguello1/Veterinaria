from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.autenticacion.models import User, UserFaceEmbedding
from apps.mascota.models import Mascota, ImagenMascota, RegistroReconocimiento
import json

@login_required
def Dashboard(request):
    user = request.user
    
    # Estadísticas generales según el rol del usuario
    if user.role in ['ADMIN', 'VET', 'OWNER']:
        # Estadísticas para administradores y veterinarios
        total_users = User.objects.filter(is_active=True).count()
        total_mascotas = Mascota.objects.count()
        mascotas_perdidas = Mascota.objects.filter(reportar_perdida=True).count()
        reconocimientos_hoy = RegistroReconocimiento.objects.filter(
            fecha__date=timezone.now().date()
        ).count()
        
        # Mascotas recientes para mostrar en tabla
        mascotas_recientes = Mascota.objects.select_related('propietario').order_by('-created_at')[:10]
    else:
        # Estadísticas para clientes (solo sus mascotas)
        total_users = 1  # Solo él mismo
        total_mascotas = user.mascotas.count()
        mascotas_perdidas = user.mascotas.filter(reportar_perdida=True).count()
        reconocimientos_hoy = RegistroReconocimiento.objects.filter(
            mascota_predicha__propietario=user,
            fecha__date=timezone.now().date()
        ).count()
        
        # Mascotas recientes del usuario
        mascotas_recientes = user.mascotas.order_by('-created_at')[:5]
    
    # Calcular mascotas activas y porcentajes
    mascotas_activas = total_mascotas - mascotas_perdidas
    
    if total_mascotas > 0:
        active_percentage = (mascotas_activas / total_mascotas) * 100
        lost_percentage = (mascotas_perdidas / total_mascotas) * 100
    else:
        active_percentage = 0
        lost_percentage = 0
    
    # Datos para el gráfico de registros por mes (últimos 6 meses)
    chart_labels = []
    chart_values = []
    
    today = timezone.now().date()
    for i in range(5, -1, -1):  # 6 meses hacia atrás
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        
        # Contar mascotas registradas en ese mes
        if user.role in ['ADMIN', 'VET', 'OWNER']:
            count = Mascota.objects.filter(
                created_at__year=month_date.year,
                created_at__month=month_date.month
            ).count()
        else:
            count = user.mascotas.filter(
                created_at__year=month_date.year,
                created_at__month=month_date.month
            ).count()
        
        chart_labels.append(month_date.strftime('%b'))
        chart_values.append(count)
    
    # Calcular tendencia (comparar último mes vs anterior)
    if len(chart_values) >= 2:
        current_month = chart_values[-1]
        previous_month = chart_values[-2]
        if previous_month > 0:
            chart_trend = ((current_month - previous_month) / previous_month) * 100
        else:
            chart_trend = 100 if current_month > 0 else 0
    else:
        chart_trend = 0
    
    # Datos para el gráfico de reconocimientos por día (últimos 7 días)
    reconocimientos_labels = []
    reconocimientos_data = []
    
    for i in range(6, -1, -1):  # 7 días hacia atrás
        day_date = today - timedelta(days=i)
        
        if user.role in ['ADMIN', 'VET', 'OWNER']:
            count = RegistroReconocimiento.objects.filter(
                fecha__date=day_date
            ).count()
        else:
            count = RegistroReconocimiento.objects.filter(
                mascota_predicha__propietario=user,
                fecha__date=day_date
            ).count()
        
        reconocimientos_labels.append(day_date.strftime('%d/%m'))
        reconocimientos_data.append(count)
    
    # Obtener estadísticas de reconocimiento facial del usuario
    facial_stats = {
        'has_biometry': False,
        'is_active': False,
        'successful_logins': 0,
        'failed_attempts': 0,
        'total_attempts': 0,
        'success_rate': 0,
        'last_login': None,
        'registered_at': None
    }
    
    try:
        face_embedding = UserFaceEmbedding.objects.get(user=user, is_active=True)
        total_attempts = face_embedding.successful_logins + face_embedding.failed_attempts
        success_rate = (face_embedding.successful_logins / total_attempts * 100) if total_attempts > 0 else 0
        
        facial_stats = {
            'has_biometry': True,
            'is_active': face_embedding.allow_login,
            'successful_logins': face_embedding.successful_logins,
            'failed_attempts': face_embedding.failed_attempts,
            'total_attempts': total_attempts,
            'success_rate': round(success_rate, 1),
            'last_login': face_embedding.last_successful_login,
            'registered_at': face_embedding.created_at
        }
    except UserFaceEmbedding.DoesNotExist:
        pass
    
    # Obtener mascotas perdidas para mostrar en cards con info de biometría
    if user.role in ['ADMIN', 'VET', 'OWNER']:
        mascotas_perdidas_cards = Mascota.objects.filter(
            reportar_perdida=True
        ).select_related('propietario').prefetch_related('imagenes')[:6]
    else:
        mascotas_perdidas_cards = user.mascotas.filter(
            reportar_perdida=True
        ).prefetch_related('imagenes')[:6]
    
    # Agregar información de biometría a cada mascota
    for mascota in mascotas_perdidas_cards:
        num_imagenes = mascota.imagenes.filter(is_biometrica=True).count()
        mascota.tiene_biometria = num_imagenes >= 5
        mascota.num_imagenes_biometricas = num_imagenes
        mascota.puede_ser_reconocida = mascota.biometria_entrenada
    
    # Breadcrumbs
    breadcrumb_list = [
        {'name': 'Dashboard', 'url': '#', 'is_active': True}
    ]
    
    context = {
        # Datos del usuario
        'user': user,
        
        # Estadísticas principales
        'total_users': total_users,
        'total_mascotas': total_mascotas,
        'mascotas_perdidas': mascotas_perdidas,
        'mascotas_activas': mascotas_activas,
        'reconocimientos_hoy': reconocimientos_hoy,
        
        # Porcentajes
        'active_percentage': active_percentage,
        'lost_percentage': lost_percentage,
        'chart_trend': chart_trend,
        
        # Datos para gráficos (convertidos a JSON para JavaScript)
        'chart_labels': json.dumps(chart_labels),
        'chart_values': chart_values,
        'reconocimientos_labels': json.dumps(reconocimientos_labels),
        'reconocimientos_data': reconocimientos_data,
        
        # Datos adicionales
        'mascotas_recientes': mascotas_recientes,
        'breadcrumb_list': breadcrumb_list,
        
        # Estadísticas de reconocimiento facial
        'facial_stats': facial_stats,
        
        # Mascotas perdidas en cards
        'mascotas_perdidas_cards': mascotas_perdidas_cards,
    }
    
    return render(request, 'layouts/dashboard.html', context)