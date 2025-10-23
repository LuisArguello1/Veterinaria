"""
Script de utilidad para crear superusuarios usando el ORM de Django
Usar con: python manage.py shell < create_superuser.py
"""

from apps.autenticacion.models import User
from django.db import IntegrityError

def create_superuser_orm(
    username,
    email,
    password,
    first_name='',
    last_name='',
    dni=None,
    direction=None,
    phone=None,
    role='ADMIN',
    specialization=None,
    license_number=None
):
    """
    Crear un superusuario usando el ORM directamente
    
    Args:
        username (str): Nombre de usuario
        email (str): Correo electrónico
        password (str): Contraseña
        first_name (str): Nombre
        last_name (str): Apellido
        dni (str): Cédula de identidad
        direction (str): Dirección
        phone (str): Teléfono
        role (str): Rol ('ADMIN', 'OWNER', 'VET')
        specialization (str): Especialización (para veterinarios)
        license_number (str): Número de licencia (para veterinarios)
    
    Returns:
        User: El usuario creado
        
    Raises:
        ValueError: Si faltan datos obligatorios o hay duplicados
        IntegrityError: Si hay problemas de integridad en la base de datos
    """
    
    # Validaciones básicas
    if not username:
        raise ValueError("El nombre de usuario es obligatorio")
    if not email:
        raise ValueError("El email es obligatorio")
    if not password:
        raise ValueError("La contraseña es obligatoria")
    
    # Verificar duplicados
    if User.objects.filter(username=username).exists():
        raise ValueError(f"El usuario '{username}' ya existe")
    
    if User.objects.filter(email=email).exists():
        raise ValueError(f"El email '{email}' ya está en uso")
    
    if dni and User.objects.filter(dni=dni).exists():
        raise ValueError(f"La cédula '{dni}' ya está en uso")
    
    # Validar rol
    valid_roles = ['ADMIN', 'OWNER', 'VET']
    if role not in valid_roles:
        raise ValueError(f"Rol inválido. Debe ser uno de: {valid_roles}")
    
    try:
        # Crear el superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            direction=direction,
            phone=phone,
            role=role,
            specialization=specialization,
            license_number=license_number,
        )
        
        print(f"✓ Superusuario '{username}' creado exitosamente")
        print(f"  - ID: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - Rol: {user.role}")
        print(f"  - Es staff: {user.is_staff}")
        print(f"  - Es superuser: {user.is_superuser}")
        
        return user
        
    except IntegrityError as e:
        raise IntegrityError(f"Error de integridad al crear el usuario: {e}")


# Ejemplo de uso:
if __name__ == "__main__":
    # Ejemplo para crear un superusuario administrador
    try:
        admin_user = create_superuser_orm(
            username='admin',
            email='admin@veterinaria.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            dni='1234567890',
            direction='Calle Principal 123',
            phone='+593987654321',
            role='ADMIN'
        )
    except (ValueError, IntegrityError) as e:
        print(f"Error: {e}")

    # Ejemplo para crear un superusuario veterinario
    try:
        vet_user = create_superuser_orm(
            username='dr_garcia',
            email='drgarcia@veterinaria.com',
            password='vet123',
            first_name='Juan',
            last_name='García',
            dni='0987654321',
            direction='Av. Veterinaria 456',
            phone='+593123456789',
            role='VET',
            specialization='Cirugía',
            license_number='VET-001'
        )
    except (ValueError, IntegrityError) as e:
        print(f"Error: {e}")