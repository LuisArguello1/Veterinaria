from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear un superusuario con todos los campos del modelo User personalizado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Correo electrónico',
        )
        parser.add_argument(
            '--first_name',
            type=str,
            help='Nombre',
        )
        parser.add_argument(
            '--last_name',
            type=str,
            help='Apellido',
        )
        parser.add_argument(
            '--dni',
            type=str,
            help='Cédula de identidad',
        )
        parser.add_argument(
            '--direction',
            type=str,
            help='Dirección',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Teléfono',
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['ADMIN', 'OWNER', 'VET'],
            default='ADMIN',
            help='Rol del usuario (ADMIN, OWNER, VET)',
        )
        parser.add_argument(
            '--specialization',
            type=str,
            help='Especialización (solo para veterinarios)',
        )
        parser.add_argument(
            '--license_number',
            type=str,
            help='Número de licencia (solo para veterinarios)',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='No solicitar entrada interactiva',
        )

    def handle(self, *args, **options):
        # Si no se proporciona --noinput, usar modo interactivo
        if not options['noinput']:
            return self.handle_interactive()
        else:
            return self.handle_non_interactive(options)

    def handle_interactive(self):
        """Manejo interactivo para crear superusuario"""
        self.stdout.write(self.style.SUCCESS('=== Creación de Superusuario ===\n'))

        # Datos obligatorios
        username = input('Nombre de usuario: ').strip()
        if not username:
            raise CommandError('El nombre de usuario es obligatorio')

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            raise CommandError(f'El usuario "{username}" ya existe')

        email = input('Correo electrónico: ').strip()
        if not email:
            raise CommandError('El correo electrónico es obligatorio')

        # Verificar si el email ya existe
        if User.objects.filter(email=email).exists():
            raise CommandError(f'El email "{email}" ya está en uso')

        password = getpass.getpass('Contraseña: ')
        if not password:
            raise CommandError('La contraseña es obligatoria')

        password_confirm = getpass.getpass('Confirmar contraseña: ')
        if password != password_confirm:
            raise CommandError('Las contraseñas no coinciden')

        # Datos opcionales
        first_name = input('Nombre (opcional): ').strip()
        last_name = input('Apellido (opcional): ').strip()
        dni = input('Cédula (opcional): ').strip()
        direction = input('Dirección (opcional): ').strip()
        phone = input('Teléfono (opcional): ').strip()

        # Rol
        self.stdout.write('\nRoles disponibles:')
        self.stdout.write('1. ADMIN - Administrador')
        self.stdout.write('2. OWNER - Dueño')
        self.stdout.write('3. VET - Veterinario')
        
        role_choice = input('Seleccionar rol (1-3, por defecto 1): ').strip()
        role_map = {'1': 'ADMIN', '2': 'OWNER', '3': 'VET', '': 'ADMIN'}
        role = role_map.get(role_choice, 'ADMIN')

        # Datos específicos para veterinarios
        specialization = None
        license_number = None
        if role == 'VET':
            specialization = input('Especialización (opcional): ').strip()
            license_number = input('Número de licencia (opcional): ').strip()

        # Verificar DNI único si se proporciona
        if dni and User.objects.filter(dni=dni).exists():
            raise CommandError(f'La cédula "{dni}" ya está en uso')

        try:
            # Crear el superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name or '',
                last_name=last_name or '',
                dni=dni or None,
                direction=direction or None,
                phone=phone or None,
                role=role,
                specialization=specialization or None,
                license_number=license_number or None,
            )

            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Superusuario "{username}" creado exitosamente')
            )
            self.stdout.write(f'  - Email: {email}')
            self.stdout.write(f'  - Rol: {role}')
            if dni:
                self.stdout.write(f'  - Cédula: {dni}')
            if role == 'VET' and specialization:
                self.stdout.write(f'  - Especialización: {specialization}')
            if role == 'VET' and license_number:
                self.stdout.write(f'  - Licencia: {license_number}')

        except IntegrityError as e:
            raise CommandError(f'Error al crear el usuario: {e}')

    def handle_non_interactive(self, options):
        """Manejo no interactivo usando argumentos de línea de comandos"""
        username = options['username']
        email = options['email']

        if not username:
            raise CommandError('--username es obligatorio')
        if not email:
            raise CommandError('--email es obligatorio')

        # Verificar unicidad
        if User.objects.filter(username=username).exists():
            raise CommandError(f'El usuario "{username}" ya existe')
        if User.objects.filter(email=email).exists():
            raise CommandError(f'El email "{email}" ya está en uso')

        dni = options.get('dni')
        if dni and User.objects.filter(dni=dni).exists():
            raise CommandError(f'La cédula "{dni}" ya está en uso')

        # Solicitar contraseña
        password = getpass.getpass('Contraseña: ')
        if not password:
            raise CommandError('La contraseña es obligatoria')

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=options.get('first_name') or '',
                last_name=options.get('last_name') or '',
                dni=dni,
                direction=options.get('direction'),
                phone=options.get('phone'),
                role=options.get('role', 'ADMIN'),
                specialization=options.get('specialization'),
                license_number=options.get('license_number'),
            )

            self.stdout.write(
                self.style.SUCCESS(f'✓ Superusuario "{username}" creado exitosamente')
            )

        except IntegrityError as e:
            raise CommandError(f'Error al crear el usuario: {e}')