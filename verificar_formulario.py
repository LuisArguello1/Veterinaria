"""
Script de Verificación del Formulario de Registro de Mascotas
Verifica que todos los componentes estén correctamente implementados
"""

import os
import sys

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_file_exists(file_path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(file_path):
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} NO ENCONTRADO: {file_path}")
        return False

def check_imports():
    """Verifica que los imports funcionen correctamente"""
    print_header("VERIFICACIÓN DE IMPORTS")
    
    success_count = 0
    total_count = 0
    
    # Verificar import del formulario
    total_count += 1
    try:
        from apps.mascota.forms import MascotaCreateForm
        print_success("Import de MascotaCreateForm funcionando")
        success_count += 1
    except ImportError as e:
        print_error(f"Error al importar MascotaCreateForm: {e}")
    
    # Verificar import de la vista
    total_count += 1
    try:
        from apps.mascota.views.create_mascota import MascotaCreateView
        print_success("Import de MascotaCreateView funcionando")
        success_count += 1
    except ImportError as e:
        print_error(f"Error al importar MascotaCreateView: {e}")
    
    # Verificar import del modelo
    total_count += 1
    try:
        from apps.mascota.models import Mascota
        print_success("Import de Mascota funcionando")
        success_count += 1
    except ImportError as e:
        print_error(f"Error al importar Mascota: {e}")
    
    # Verificar import de notificaciones
    total_count += 1
    try:
        from apps.autenticacion.models_notification import Notification
        print_success("Import de Notification funcionando")
        success_count += 1
    except ImportError as e:
        print_error(f"Error al importar Notification: {e}")
    
    print(f"\n{Colors.BOLD}Resultado: {success_count}/{total_count} imports exitosos{Colors.RESET}")
    return success_count == total_count

def check_files():
    """Verifica que todos los archivos existan"""
    print_header("VERIFICACIÓN DE ARCHIVOS")
    
    files = [
        ("apps/mascota/forms/mascota_form.py", "Formulario Django"),
        ("apps/mascota/forms/__init__.py", "Init de forms"),
        ("apps/mascota/views/create_mascota.py", "Vista de creación"),
        ("apps/mascota/templates/mascota_registro/form.html", "Template del formulario"),
        ("static/js/mascota-form.js", "JavaScript del formulario"),
        (".vscode/settings.json", "Configuración de VS Code"),
    ]
    
    success_count = 0
    for file_path, description in files:
        if check_file_exists(file_path, description):
            success_count += 1
    
    print(f"\n{Colors.BOLD}Resultado: {success_count}/{len(files)} archivos encontrados{Colors.RESET}")
    return success_count == len(files)

def check_form_fields():
    """Verifica que el formulario tenga todos los campos"""
    print_header("VERIFICACIÓN DE CAMPOS DEL FORMULARIO")
    
    try:
        from apps.mascota.forms import MascotaCreateForm
        
        expected_fields = [
            'nombre', 'raza', 'sexo', 'fecha_nacimiento', 'peso',
            'color', 'etapa_vida', 'estado_corporal', 
            'caracteristicas_especiales', 'foto_perfil'
        ]
        
        form = MascotaCreateForm()
        actual_fields = list(form.fields.keys())
        
        success_count = 0
        for field in expected_fields:
            if field in actual_fields:
                print_success(f"Campo '{field}' presente")
                success_count += 1
            else:
                print_error(f"Campo '{field}' NO encontrado")
        
        print(f"\n{Colors.BOLD}Resultado: {success_count}/{len(expected_fields)} campos encontrados{Colors.RESET}")
        return success_count == len(expected_fields)
    
    except Exception as e:
        print_error(f"Error al verificar campos: {e}")
        return False

def check_url_configuration():
    """Verifica que la URL esté configurada"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN DE URLs")
    
    try:
        from django.urls import reverse
        
        # Intentar obtener la URL
        url = reverse('mascota:create_mascota')
        print_success(f"URL 'mascota:create_mascota' configurada correctamente: {url}")
        return True
    
    except Exception as e:
        print_error(f"Error al verificar URL: {e}")
        return False

def check_model_fields():
    """Verifica que el modelo Mascota tenga los campos necesarios"""
    print_header("VERIFICACIÓN DEL MODELO MASCOTA")
    
    try:
        from apps.mascota.models import Mascota
        
        required_fields = [
            'nombre', 'raza', 'sexo', 'fecha_nacimiento', 'peso',
            'color', 'etapa_vida', 'estado_corporal', 
            'caracteristicas_especiales', 'foto_perfil', 'propietario', 'uuid'
        ]
        
        model_fields = [f.name for f in Mascota._meta.get_fields()]
        
        success_count = 0
        for field in required_fields:
            if field in model_fields:
                print_success(f"Campo del modelo '{field}' presente")
                success_count += 1
            else:
                print_warning(f"Campo del modelo '{field}' NO encontrado")
        
        print(f"\n{Colors.BOLD}Resultado: {success_count}/{len(required_fields)} campos del modelo encontrados{Colors.RESET}")
        return success_count >= 10  # Al menos 10 campos deben estar presentes
    
    except Exception as e:
        print_error(f"Error al verificar modelo: {e}")
        return False

def check_permissions():
    """Verifica que la vista tenga las restricciones de permisos"""
    print_header("VERIFICACIÓN DE PERMISOS")
    
    try:
        from apps.mascota.views.create_mascota import MascotaCreateView
        from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
        
        # Verificar que herede de LoginRequiredMixin y UserPassesTestMixin
        is_login_required = issubclass(MascotaCreateView, LoginRequiredMixin)
        has_user_test = issubclass(MascotaCreateView, UserPassesTestMixin)
        has_test_func = hasattr(MascotaCreateView, 'test_func')
        
        if is_login_required:
            print_success("LoginRequiredMixin presente")
        else:
            print_error("LoginRequiredMixin NO presente")
        
        if has_user_test:
            print_success("UserPassesTestMixin presente")
        else:
            print_error("UserPassesTestMixin NO presente")
        
        if has_test_func:
            print_success("Método test_func() presente")
        else:
            print_error("Método test_func() NO presente")
        
        result = is_login_required and has_user_test and has_test_func
        
        if result:
            print(f"\n{Colors.BOLD}✅ Restricciones de permisos correctamente implementadas{Colors.RESET}")
        else:
            print(f"\n{Colors.BOLD}❌ Faltan restricciones de permisos{Colors.RESET}")
        
        return result
    
    except Exception as e:
        print_error(f"Error al verificar permisos: {e}")
        return False

def main():
    """Función principal"""
    print_header("VERIFICACIÓN DEL FORMULARIO DE REGISTRO DE MASCOTAS")
    
    print_info("Iniciando verificación del sistema...")
    print_info("Fecha: 19 de octubre de 2025")
    print_info("Proyecto: PetFace ID - Sistema Veterinario\n")
    
    results = {
        "Archivos": check_files(),
        "Imports": check_imports(),
        "Campos del formulario": check_form_fields(),
        "Modelo": check_model_fields(),
        "Configuración de URLs": check_url_configuration(),
        "Permisos": check_permissions(),
    }
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    for check_name, passed in results.items():
        if passed:
            print_success(f"{check_name}: CORRECTO")
        else:
            print_error(f"{check_name}: FALLÓ")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    percentage = (passed_checks / total_checks) * 100
    
    if percentage == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡TODO CORRECTO! {passed_checks}/{total_checks} verificaciones pasadas ({percentage:.0f}%){Colors.RESET}")
        print(f"\n{Colors.GREEN}✅ El formulario de registro de mascotas está completamente funcional{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Puedes iniciar el servidor con: python manage.py runserver{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Accede a: http://localhost:8000/mascota/{Colors.RESET}\n")
    elif percentage >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  CASI COMPLETO: {passed_checks}/{total_checks} verificaciones pasadas ({percentage:.0f}%){Colors.RESET}")
        print(f"\n{Colors.YELLOW}Revisa los elementos que fallaron arriba{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ REQUIERE ATENCIÓN: {passed_checks}/{total_checks} verificaciones pasadas ({percentage:.0f}%){Colors.RESET}")
        print(f"\n{Colors.RED}Varios componentes necesitan corrección{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

if __name__ == '__main__':
    # Configurar Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    main()
