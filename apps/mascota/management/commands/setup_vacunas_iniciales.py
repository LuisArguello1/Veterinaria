"""
Comando para crear vacunas estándar y datos de prueba
Uso: python manage.py setup_vacunas_iniciales
"""
from django.core.management.base import BaseCommand
from apps.mascota.models_historial import Vacuna, RegistroVacuna, HistorialMedico
from apps.mascota.models import Mascota
from apps.autenticacion.models import User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Crea vacunas estándar y datos de prueba del historial médico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creando vacunas estándar...'))
        
        # Vacunas para perros
        vacunas_perros = [
            {
                'nombre': 'Parvovirus',
                'descripcion': 'Protege contra el parvovirus canino',
                'frecuencia_meses': 12,
                'edad_minima_meses': 2,
                'apta_para_perros': True,
                'apta_para_gatos': False,
                'obligatoria': True,
            },
            {
                'nombre': 'Moquillo',
                'descripcion': 'Protege contra el virus del moquillo canino',
                'frecuencia_meses': 12,
                'edad_minima_meses': 2,
                'apta_para_perros': True,
                'apta_para_gatos': False,
                'obligatoria': True,
            },
            {
                'nombre': 'Rabia',
                'descripcion': 'Vacuna antirrábica obligatoria',
                'frecuencia_meses': 12,
                'edad_minima_meses': 3,
                'apta_para_perros': True,
                'apta_para_gatos': True,
                'obligatoria': True,
            },
            {
                'nombre': 'Hepatitis Canina',
                'descripcion': 'Protege contra la hepatitis infecciosa canina',
                'frecuencia_meses': 12,
                'edad_minima_meses': 2,
                'apta_para_perros': True,
                'apta_para_gatos': False,
                'obligatoria': False,
            },
            {
                'nombre': 'Leptospirosis',
                'descripcion': 'Protege contra la leptospirosis',
                'frecuencia_meses': 12,
                'edad_minima_meses': 3,
                'apta_para_perros': True,
                'apta_para_gatos': False,
                'obligatoria': False,
            },
            {
                'nombre': 'Tos de las Perreras',
                'descripcion': 'Protege contra la traqueobronquitis infecciosa',
                'frecuencia_meses': 12,
                'edad_minima_meses': 3,
                'apta_para_perros': True,
                'apta_para_gatos': False,
                'obligatoria': False,
            },
        ]
        
        # Vacunas para gatos
        vacunas_gatos = [
            {
                'nombre': 'Panleucopenia Felina',
                'descripcion': 'Protege contra la panleucopenia (moquillo felino)',
                'frecuencia_meses': 12,
                'edad_minima_meses': 2,
                'apta_para_perros': False,
                'apta_para_gatos': True,
                'obligatoria': True,
            },
            {
                'nombre': 'Rinotraqueítis Felina',
                'descripcion': 'Protege contra herpesvirus felino',
                'frecuencia_meses': 12,
                'edad_minima_meses': 2,
                'apta_para_perros': False,
                'apta_para_gatos': True,
                'obligatoria': True,
            },
            {
                'nombre': 'Calicivirus Felino',
                'descripcion': 'Protege contra el calicivirus felino',
                'frecuencia_meses': 12,
                'edad_minima_meses': 2,
                'apta_para_perros': False,
                'apta_para_gatos': True,
                'obligatoria': True,
            },
            {
                'nombre': 'Leucemia Felina',
                'descripcion': 'Protege contra el virus de la leucemia felina',
                'frecuencia_meses': 12,
                'edad_minima_meses': 3,
                'apta_para_perros': False,
                'apta_para_gatos': True,
                'obligatoria': False,
            },
        ]
        
        vacunas_creadas = 0
        for vacuna_data in vacunas_perros + vacunas_gatos:
            vacuna, created = Vacuna.objects.get_or_create(
                nombre=vacuna_data['nombre'],
                defaults=vacuna_data
            )
            if created:
                vacunas_creadas += 1
                self.stdout.write(f'  ✓ Vacuna creada: {vacuna.nombre}')
            else:
                self.stdout.write(f'  - Vacuna ya existe: {vacuna.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total vacunas en sistema: {Vacuna.objects.count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Vacunas nuevas creadas: {vacunas_creadas}')
        )
        
        # Crear algunos registros de prueba
        self.stdout.write(self.style.WARNING('\nCreando registros de prueba...'))
        
        mascotas = Mascota.objects.all()[:3]  # Primeras 3 mascotas
        veterinarios = User.objects.filter(role='VET')
        
        if mascotas.exists() and veterinarios.exists():
            vet = veterinarios.first()
            count_registros = 0
            
            for mascota in mascotas:
                # Vacuna de rabia aplicada hace 11 meses (próxima en 1 mes)
                vacuna_rabia = Vacuna.objects.filter(nombre='Rabia').first()
                if vacuna_rabia and not RegistroVacuna.objects.filter(mascota=mascota, vacuna=vacuna_rabia).exists():
                    fecha_aplicacion = timezone.now().date() - timedelta(days=330)  # 11 meses
                    fecha_proxima = fecha_aplicacion + timedelta(days=365)  # En 1 mes
                    
                    RegistroVacuna.objects.create(
                        mascota=mascota,
                        vacuna=vacuna_rabia,
                        fecha_aplicacion=fecha_aplicacion,
                        fecha_proxima=fecha_proxima,
                        veterinario=vet,
                        lote='LOTE-2024-001'
                    )
                    count_registros += 1
                    self.stdout.write(f'  ✓ Vacuna aplicada: {mascota.nombre} - {vacuna_rabia.nombre}')
                
                # Consulta de revisión general
                if not HistorialMedico.objects.filter(mascota=mascota, tipo_evento='revision').exists():
                    HistorialMedico.objects.create(
                        mascota=mascota,
                        veterinario=vet,
                        tipo_evento='revision',
                        titulo='Revisión General Anual',
                        descripcion='Chequeo completo de salud. Mascota en excelente condición.',
                        fecha_evento=timezone.now().date() - timedelta(days=30),
                        fecha_proxima=timezone.now().date() + timedelta(days=335),  # En 11 meses
                        estado='completado',
                        notas='Todo en orden. Se recomienda mantener dieta balanceada.',
                        dias_anticipacion_recordatorio=30
                    )
                    count_registros += 1
                    self.stdout.write(f'  ✓ Consulta registrada: {mascota.nombre} - Revisión General')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Registros de prueba creados: {count_registros}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No hay mascotas o veterinarios para crear registros de prueba')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ ¡Proceso completado exitosamente!')
        )
