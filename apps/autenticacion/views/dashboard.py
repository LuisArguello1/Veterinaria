from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.autenticacion.models import User
from apps.mascota.models import Mascota, ImagenMascota, RegistroReconocimiento
import json

@login_required
def Dashboard(request):
    user = request.user
    
    # Estadísticas generales según el rol del usuario
    if user.role in ['ADMIN', 'VET']:
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
        if user.role in ['ADMIN', 'VET']:
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
        
        if user.role in ['ADMIN', 'VET']:
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
    }
    
    return render(request, 'layouts/dashboard.html', context)