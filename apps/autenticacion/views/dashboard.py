from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from apps.autenticacion.models import User
from apps.mascota.models import Mascota, ModeloGlobal, RegistroReconocimiento, ImagenMascota

@login_required
def Dashboard(request):
    user = request.user
    context = {}
    
    # Información básica del usuario
    context['user'] = user
    context['role'] = user.role
    
    try:
        # Métricas específicas del usuario actual
        if user.is_owner:
            # Para propietarios - métricas personales
            context['mis_mascotas'] = user.mascotas.count()
            context['mis_mascotas_entrenadas'] = user.mascotas.filter(biometria_entrenada=True).count()
            context['mis_mascotas_perdidas'] = user.mascotas.filter(reportar_perdida=True).count()
            context['total_imagenes'] = ImagenMascota.objects.filter(mascota__propietario=user).count()
            
            # Última mascota registrada
            context['ultima_mascota'] = user.mascotas.order_by('-created_at').first()
            
            # Reconocimientos recientes de mis mascotas
            context['reconocimientos_recientes'] = RegistroReconocimiento.objects.filter(
                mascota_predicha__propietario=user
            ).order_by('-fecha')[:3]
            
            # Progreso de entrenamiento
            if context['mis_mascotas'] > 0:
                context['progreso_entrenamiento'] = round(
                    (context['mis_mascotas_entrenadas'] / context['mis_mascotas']) * 100, 1
                )
            else:
                context['progreso_entrenamiento'] = 0
                
        elif user.is_vet or user.is_admin:
            # Para veterinarios y administradores - métricas del sistema
            context['total_mascotas'] = Mascota.objects.count()
            context['total_usuarios'] = User.objects.filter(role='OWNER').count()
            context['mascotas_entrenadas'] = Mascota.objects.filter(biometria_entrenada=True).count()
            context['mascotas_perdidas'] = Mascota.objects.filter(reportar_perdida=True).count()
            
            # Actividad reciente
            hoy = timezone.now().date()
            hace_7_dias = hoy - timedelta(days=7)
            
            context['mascotas_nuevas_semana'] = Mascota.objects.filter(
                created_at__date__gte=hace_7_dias
            ).count()
            
            context['reconocimientos_hoy'] = RegistroReconocimiento.objects.filter(
                fecha__date=hoy
            ).count()
            
            # Modelo activo
            context['modelo_activo'] = ModeloGlobal.get_active_model()
            
            # Usuarios más activos (top 3)
            context['usuarios_activos'] = User.objects.filter(
                mascotas__isnull=False
            ).annotate(
                num_mascotas=Count('mascotas')
            ).order_by('-num_mascotas')[:3]
            
    except Exception as e:
        # Manejo de errores
        messages.warning(request, 'Algunos datos del dashboard no están disponibles en este momento.')
        # Valores por defecto según el rol
        if user.is_owner:
            context.update({
                'mis_mascotas': 0,
                'mis_mascotas_entrenadas': 0,
                'mis_mascotas_perdidas': 0,
                'total_imagenes': 0,
                'progreso_entrenamiento': 0
            })
        else:
            context.update({
                'total_mascotas': 0,
                'total_usuarios': 0,
                'mascotas_entrenadas': 0,
                'mascotas_perdidas': 0,
                'mascotas_nuevas_semana': 0,
                'reconocimientos_hoy': 0
            })
    
    return render(request, 'layouts/dashboard.html', context)