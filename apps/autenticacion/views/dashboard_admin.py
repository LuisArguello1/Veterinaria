"""
Vista del Dashboard Administrativo
Proporciona estadísticas completas y métricas del sistema para administradores
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta
import json

from apps.autenticacion.models import User, UserFaceEmbedding, Notification
from apps.mascota.models import Mascota, ImagenMascota, RegistroReconocimiento


def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and user.role == 'ADMIN'


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_dashboard(request):
    """
    Dashboard administrativo con estadísticas completas del sistema
    """
    
    # ==================== ESTADÍSTICAS GENERALES ====================
    
    # Usuarios
    total_usuarios = User.objects.filter(is_active=True).count()
    usuarios_con_facial = UserFaceEmbedding.objects.filter(is_active=True).count()
    nuevos_usuarios_mes = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Mascotas
    total_mascotas = Mascota.objects.count()
    mascotas_perdidas = Mascota.objects.filter(reportar_perdida=True).count()
    mascotas_con_biometria = Mascota.objects.filter(biometria_entrenada=True).count()
    nuevas_mascotas_mes = Mascota.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Reconocimientos/Escaneos
    reconocimientos_hoy = RegistroReconocimiento.objects.filter(
        fecha__date=timezone.now().date()
    ).count()
    
    reconocimientos_mes = RegistroReconocimiento.objects.filter(
        fecha__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Tasa de éxito de reconocimientos
    reconocimientos_exitosos = RegistroReconocimiento.objects.filter(exito=True).count()
    total_reconocimientos = RegistroReconocimiento.objects.count()
    tasa_exito = (reconocimientos_exitosos / total_reconocimientos * 100) if total_reconocimientos > 0 else 0
    
    # Tiempo promedio de procesamiento
    tiempo_promedio = RegistroReconocimiento.objects.filter(
        tiempo_procesamiento__isnull=False
    ).aggregate(Avg('tiempo_procesamiento'))['tiempo_procesamiento__avg'] or 0
    
    # Notificaciones
    notificaciones_sin_leer = Notification.objects.filter(is_read=False).count()
    notificaciones_mes = Notification.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Imágenes biométricas
    total_imagenes = ImagenMascota.objects.filter(is_biometrica=True).count()
    
    
    # ==================== GRÁFICO 1: TOP 10 RAZAS ====================
    
    razas_top = Mascota.objects.filter(
        raza__isnull=False
    ).exclude(
        raza=''
    ).values('raza').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')[:10]
    
    razas_labels = [r['raza'] for r in razas_top]
    razas_values = [r['cantidad'] for r in razas_top]
    
    
    # ==================== GRÁFICO 2: ESCANEOS DIARIOS (30 DÍAS) ====================
    
    hoy = timezone.now().date()
    escaneos_diarios_labels = []
    escaneos_diarios_values = []
    
    for i in range(29, -1, -1):  # 30 días hacia atrás
        fecha = hoy - timedelta(days=i)
        count = RegistroReconocimiento.objects.filter(fecha__date=fecha).count()
        escaneos_diarios_labels.append(fecha.strftime('%d/%m'))
        escaneos_diarios_values.append(count)
    
    
    # ==================== GRÁFICO 3: DISTRIBUCIÓN POR ETAPA DE VIDA ====================
    
    etapas_vida = Mascota.objects.filter(
        etapa_vida__isnull=False
    ).values('etapa_vida').annotate(
        cantidad=Count('id')
    ).order_by('etapa_vida')
    
    etapas_labels = []
    etapas_values = []
    etapas_colors = {
        'cachorro': '#3b82f6',  # Azul
        'joven': '#10b981',     # Verde
        'adulto': '#f59e0b',    # Amarillo
        'senior': '#8b5cf6'     # Púrpura
    }
    etapas_bg_colors = []
    
    for etapa in etapas_vida:
        etapa_nombre = etapa['etapa_vida'].capitalize()
        etapas_labels.append(etapa_nombre)
        etapas_values.append(etapa['cantidad'])
        etapas_bg_colors.append(etapas_colors.get(etapa['etapa_vida'], '#6b7280'))
    
    
    # ==================== GRÁFICO 4: DISTRIBUCIÓN POR ESTADO CORPORAL ====================
    
    estados_corporales = Mascota.objects.filter(
        estado_corporal__isnull=False
    ).values('estado_corporal').annotate(
        cantidad=Count('id')
    ).order_by('estado_corporal')
    
    estados_labels = []
    estados_values = []
    estados_colors_map = {
        'delgado': '#ef4444',   # Rojo
        'normal': '#10b981',    # Verde
        'obeso': '#f59e0b'      # Naranja
    }
    estados_bg_colors = []
    
    for estado in estados_corporales:
        estado_nombre = estado['estado_corporal'].capitalize()
        estados_labels.append(estado_nombre)
        estados_values.append(estado['cantidad'])
        estados_bg_colors.append(estados_colors_map.get(estado['estado_corporal'], '#6b7280'))
    
    
    # ==================== GRÁFICO 5: REGISTROS DE MASCOTAS POR MES (6 MESES) ====================
    
    registros_mes_labels = []
    registros_mes_values = []
    
    for i in range(5, -1, -1):  # 6 meses hacia atrás
        mes_fecha = hoy.replace(day=1) - timedelta(days=30 * i)
        count = Mascota.objects.filter(
            created_at__year=mes_fecha.year,
            created_at__month=mes_fecha.month
        ).count()
        registros_mes_labels.append(mes_fecha.strftime('%b %Y'))
        registros_mes_values.append(count)
    
    
    # ==================== GRÁFICO 6: ACTIVIDAD POR HORA DEL DÍA ====================
    
    # Obtener reconocimientos de los últimos 30 días con la hora
    reconocimientos_por_hora = RegistroReconocimiento.objects.filter(
        fecha__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        hora=ExtractHour('fecha')
    ).values('hora').annotate(
        cantidad=Count('id')
    ).order_by('hora')
    
    # Crear array de 24 horas (0-23)
    horas_labels = [f'{h:02d}:00' for h in range(24)]
    horas_values = [0] * 24
    
    for rec in reconocimientos_por_hora:
        hora = rec['hora']
        horas_values[hora] = rec['cantidad']
    
    
    # ==================== GRÁFICO 7: USUARIOS POR ROL ====================
    
    usuarios_por_rol = User.objects.filter(
        is_active=True
    ).values('role').annotate(
        cantidad=Count('id')
    ).order_by('role')
    
    roles_labels = []
    roles_values = []
    roles_colors_map = {
        'ADMIN': '#ef4444',     # Rojo
        'VET': '#8b5cf6',       # Púrpura
        'OWNER': '#3b82f6'      # Azul
    }
    roles_bg_colors = []
    
    for rol in usuarios_por_rol:
        rol_display = {
            'ADMIN': 'Administrador',
            'VET': 'Veterinario',
            'OWNER': 'Propietario'
        }.get(rol['role'], rol['role'])
        
        roles_labels.append(rol_display)
        roles_values.append(rol['cantidad'])
        roles_bg_colors.append(roles_colors_map.get(rol['role'], '#6b7280'))
    
    
    # ==================== GRÁFICO 8: TASA DE ÉXITO DE RECONOCIMIENTOS (30 DÍAS) ====================
    
    reconocimientos_por_dia = []
    for i in range(29, -1, -1):
        fecha = hoy - timedelta(days=i)
        total_dia = RegistroReconocimiento.objects.filter(fecha__date=fecha).count()
        exitosos_dia = RegistroReconocimiento.objects.filter(fecha__date=fecha, exito=True).count()
        tasa_dia = (exitosos_dia / total_dia * 100) if total_dia > 0 else 0
        reconocimientos_por_dia.append(tasa_dia)
    
    
    # ==================== DISTRIBUCIÓN POR SEXO ====================
    
    mascotas_por_sexo = Mascota.objects.filter(
        sexo__isnull=False
    ).values('sexo').annotate(
        cantidad=Count('id')
    )
    
    sexo_labels = []
    sexo_values = []
    for sexo in mascotas_por_sexo:
        sexo_display = 'Macho' if sexo['sexo'] == 'macho' else 'Hembra'
        sexo_labels.append(sexo_display)
        sexo_values.append(sexo['cantidad'])
    
    
    # ==================== TOP 5 MASCOTAS MÁS RECONOCIDAS ====================
    
    mascotas_mas_reconocidas = RegistroReconocimiento.objects.filter(
        mascota_predicha__isnull=False,
        exito=True
    ).values(
        'mascota_predicha__nombre',
        'mascota_predicha__raza'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    
    # ==================== USUARIOS MÁS ACTIVOS ====================
    
    usuarios_activos = RegistroReconocimiento.objects.filter(
        usuario__isnull=False
    ).values(
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    
    # ==================== NOTIFICACIONES POR CATEGORÍA ====================
    
    notificaciones_por_categoria = Notification.objects.values(
        'category'
    ).annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')
    
    notif_cat_labels = []
    notif_cat_values = []
    for notif in notificaciones_por_categoria:
        categoria_display = {
            'SYSTEM': 'Sistema',
            'MASCOTA': 'Mascota',
            'USUARIO': 'Usuario',
            'BIOMETRIA': 'Biometría',
            'PERDIDA': 'Perdida',
            'ENCONTRADA': 'Encontrada',
            'VACUNA': 'Vacuna',
            'CONSULTA': 'Consulta',
            'OTRO': 'Otro'
        }.get(notif['category'], notif['category'])
        notif_cat_labels.append(categoria_display)
        notif_cat_values.append(notif['cantidad'])
    
    
    # ==================== CONTEXT ====================
    
    context = {
        # Estadísticas principales
        'total_usuarios': total_usuarios,
        'usuarios_con_facial': usuarios_con_facial,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
        'total_mascotas': total_mascotas,
        'mascotas_perdidas': mascotas_perdidas,
        'mascotas_con_biometria': mascotas_con_biometria,
        'nuevas_mascotas_mes': nuevas_mascotas_mes,
        'reconocimientos_hoy': reconocimientos_hoy,
        'reconocimientos_mes': reconocimientos_mes,
        'tasa_exito': round(tasa_exito, 1),
        'tiempo_promedio': round(tiempo_promedio, 2) if tiempo_promedio else 0,
        'notificaciones_sin_leer': notificaciones_sin_leer,
        'notificaciones_mes': notificaciones_mes,
        'total_imagenes': total_imagenes,
        
        # Gráfico 1: Top Razas
        'razas_labels': json.dumps(razas_labels),
        'razas_values': razas_values,
        
        # Gráfico 2: Escaneos diarios
        'escaneos_diarios_labels': json.dumps(escaneos_diarios_labels),
        'escaneos_diarios_values': escaneos_diarios_values,
        
        # Gráfico 3: Etapas de vida
        'etapas_labels': json.dumps(etapas_labels),
        'etapas_values': etapas_values,
        'etapas_colors': json.dumps(etapas_bg_colors),
        
        # Gráfico 4: Estado corporal
        'estados_labels': json.dumps(estados_labels),
        'estados_values': estados_values,
        'estados_colors': json.dumps(estados_bg_colors),
        
        # Gráfico 5: Registros por mes
        'registros_mes_labels': json.dumps(registros_mes_labels),
        'registros_mes_values': registros_mes_values,
        
        # Gráfico 6: Actividad por hora
        'horas_labels': json.dumps(horas_labels),
        'horas_values': horas_values,
        
        # Gráfico 7: Usuarios por rol
        'roles_labels': json.dumps(roles_labels),
        'roles_values': roles_values,
        'roles_colors': json.dumps(roles_bg_colors),
        
        # Gráfico 8: Tasa de éxito
        'reconocimientos_tasa_exito': reconocimientos_por_dia,
        'reconocimientos_tasa_labels': json.dumps(escaneos_diarios_labels),
        
        # Distribución por sexo
        'sexo_labels': json.dumps(sexo_labels),
        'sexo_values': sexo_values,
        
        # Top mascotas y usuarios
        'mascotas_mas_reconocidas': mascotas_mas_reconocidas,
        'usuarios_activos': usuarios_activos,
        
        # Notificaciones por categoría
        'notif_cat_labels': json.dumps(notif_cat_labels),
        'notif_cat_values': notif_cat_values,
        
        # Porcentajes calculados
        'porcentaje_biometria': round((mascotas_con_biometria / total_mascotas * 100), 1) if total_mascotas > 0 else 0,
        'porcentaje_facial': round((usuarios_con_facial / total_usuarios * 100), 1) if total_usuarios > 0 else 0,
        
        # Breadcrumbs
        'breadcrumb_list': [
            {'name': 'Dashboard', 'url': '/dashboard/', 'is_active': False},
            {'name': 'Dashboard Admin', 'url': '#', 'is_active': True}
        ],
    }
    
    return render(request, 'autenticacion/admin/dashboard_admin.html', context)
