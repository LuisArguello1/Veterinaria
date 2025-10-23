"""
Comando para crear notificaciones de prueba
Uso: python manage.py create_test_notifications
"""
from django.core.management.base import BaseCommand
from apps.autenticacion.models import User
from apps.autenticacion.models_notification import Notification


class Command(BaseCommand):
    help = 'Crea notificaciones de prueba para testing'

    def handle(self, *args, **options):
        # Obtener todos los usuarios activos
        usuarios = User.objects.filter(is_active=True)
        
        if not usuarios.exists():
            self.stdout.write(self.style.ERROR('No hay usuarios activos en el sistema'))
            return
        
        # Notificaciones de prueba por tipo
        notificaciones_prueba = [
            {
                'titulo': '¡Bienvenido al sistema PetFace ID!',
                'mensaje': 'Gracias por unirte a nuestra plataforma de gestión veterinaria. Aquí podrás gestionar toda la información de tus mascotas de forma segura.',
                'tipo': 'SUCCESS',
            },
            {
                'titulo': 'Recordatorio: Vacunación pendiente',
                'mensaje': 'No olvides que tu mascota tiene una vacuna programada para los próximos días. Consulta con tu veterinario.',
                'tipo': 'REMINDER',
                'url_accion': '/mascota/main_register/',
                'texto_accion': 'Ver mis mascotas',
            },
            {
                'titulo': 'Actualización del sistema',
                'mensaje': 'Hemos añadido nuevas funcionalidades al sistema de reconocimiento biométrico. Ahora podrás entrenar modelos con mayor precisión.',
                'tipo': 'INFO',
            },
            {
                'titulo': 'Atención: Revisa tu perfil',
                'mensaje': 'Hemos detectado que algunos campos de tu perfil están incompletos. Por favor, actualiza tu información.',
                'tipo': 'WARNING',
                'url_accion': '/auth/profile/edit/',
                'texto_accion': 'Actualizar perfil',
            },
            {
                'titulo': 'Nueva mascota registrada',
                'mensaje': 'Se ha completado el registro de tu nueva mascota en el sistema. Ya puedes acceder a todas las funcionalidades.',
                'tipo': 'SUCCESS',
            },
            {
                'titulo': 'Sistema de QR actualizado',
                'mensaje': 'El sistema de códigos QR ha sido mejorado. Ahora puedes generar códigos personalizados para cada mascota.',
                'tipo': 'INFO',
                'icono': 'pi-qrcode',
            },
        ]
        
        count = 0
        for usuario in usuarios:
            for notif_data in notificaciones_prueba:
                Notification.objects.create(
                    usuario=usuario,
                    **notif_data
                )
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Se crearon {count} notificaciones para {usuarios.count()} usuario(s)'
            )
        )
        
        # Resumen por tipo
        self.stdout.write('\nResumen por tipo:')
        for tipo, label in Notification.TIPO_CHOICES:
            total = Notification.objects.filter(tipo=tipo).count()
            if total > 0:
                self.stdout.write(f'  - {label}: {total} notificaciones')
