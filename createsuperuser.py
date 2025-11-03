#!/usr/bin/env python
"""
Script para crear un superusuario automáticamente
usando el modelo personalizado de usuario
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.autenticacion.models import User

def create_superuser():
    """Crear un superusuario con datos predefinidos"""
    
    # Datos del superusuario
    username = 'Admin'
    email = 'admin@gmail.com'
    password = 'admin123'
    first_name = 'Administrador'
    last_name = 'Sistema'
    dni = '0921235651'
    phone = '0987654321'
    direction = 'Dirección de la Veterinaria'
    
    try:
        # Verificar si ya existe un superusuario con ese username
        if User.objects.filter(username=username).exists():
            print(f"❌ El usuario '{username}' ya existe.")
            user = User.objects.get(username=username)
            print(f"📋 Datos actuales:")
            print(f"   - Username: {user.username}")
            print(f"   - Email: {user.email}")
            print(f"   - Nombre: {user.first_name} {user.last_name}")
            print(f"   - DNI: {user.dni}")
            print(f"   - Rol: {user.get_role_display()}")
            print(f"   - Es superusuario: {user.is_superuser}")
            print(f"   - Es staff: {user.is_staff}")
            return False
        
        # Crear el superusuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            phone=phone,
            direction=direction,
            role=User.Role.ADMIN
        )
        
        # Asignar permisos de superusuario
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print("✅ Superusuario creado exitosamente!")
        print("📋 Datos del nuevo superusuario:")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Password: {password}")
        print(f"   - Nombre: {user.first_name} {user.last_name}")
        print(f"   - DNI: {user.dni}")
        print(f"   - Teléfono: {user.phone}")
        print(f"   - Dirección: {user.direction}")
        print(f"   - Rol: {user.get_role_display()}")
        print(f"   - Es superusuario: {user.is_superuser}")
        print(f"   - Es staff: {user.is_staff}")
        print("\n🔐 Credenciales de acceso:")
        print(f"   Email: {user.email}")
        print(f"   Contraseña: {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear el superusuario: {e}")
        return False

def create_custom_superuser():
    """Crear un superusuario con datos personalizados"""
    
    print("📝 Creación de superusuario personalizado")
    print("=" * 45)
    
    try:
        # Solicitar datos al usuario
        username = input("Username: ").strip()
        if not username:
            print("❌ El username es obligatorio")
            return False
        
        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            print(f"❌ El usuario '{username}' ya existe.")
            return False
        
        email = input("Email: ").strip()
        if not email:
            print("❌ El email es obligatorio")
            return False
        
        password = input("Password: ").strip()
        if not password:
            print("❌ La contraseña es obligatoria")
            return False
        
        first_name = input("Nombre (opcional): ").strip()
        last_name = input("Apellido (opcional): ").strip()
        dni = input("DNI/Cédula (opcional): ").strip()
        phone = input("Teléfono (opcional): ").strip()
        direction = input("Dirección (opcional): ").strip()
        
        # Crear el usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dni=dni if dni else "0943986778",
            phone=phone if phone else "00000000",
            direction=direction if direction else "No colocada",
            role=User.Role.ADMIN
        )
        
        # Asignar permisos de superusuario
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print("\n✅ Superusuario personalizado creado exitosamente!")
        print("📋 Datos del nuevo superusuario:")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Nombre: {user.first_name} {user.last_name}")
        print(f"   - DNI: {user.dni}")
        print(f"   - Teléfono: {user.phone}")
        print(f"   - Dirección: {user.direction}")
        print(f"   - Rol: {user.get_role_display()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear el superusuario: {e}")
        return False

def list_superusers():
    """Listar todos los superusuarios existentes"""
    
    print("👑 Lista de superusuarios existentes:")
    print("=" * 40)
    
    superusers = User.objects.filter(is_superuser=True)
    
    if not superusers.exists():
        print("❌ No hay superusuarios registrados")
        return
    
    for i, user in enumerate(superusers, 1):
        print(f"\n{i}. {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Nombre: {user.first_name} {user.last_name}")
        print(f"   - DNI: {user.dni}")
        print(f"   - Rol: {user.get_role_display()}")
        print(f"   - Activo: {'Sí' if user.is_active else 'No'}")
        print(f"   - Staff: {'Sí' if user.is_staff else 'No'}")

def main():
    """Función principal del script"""
    
    print("🏥 Sistema de Gestión Veterinaria")
    print("🔧 Creador de Superusuarios")
    print("=" * 50)
    
    while True:
        print("\n📋 Opciones disponibles:")
        print("1. Crear superusuario con datos predefinidos")
        print("2. Crear superusuario personalizado")
        print("3. Listar superusuarios existentes")
        print("4. Salir")
        
        try:
            option = input("\nSelecciona una opción (1-4): ").strip()
            
            if option == '1':
                print("\n🚀 Creando superusuario predefinido...")
                create_superuser()
            
            elif option == '2':
                print("\n🎯 Creando superusuario personalizado...")
                create_custom_superuser()
            
            elif option == '3':
                print("\n📊 Listando superusuarios...")
                list_superusers()
            
            elif option == '4':
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción no válida. Por favor, selecciona 1, 2, 3 o 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario.")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()
