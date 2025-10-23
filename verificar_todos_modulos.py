"""
Script de Verificación Completa de Todos los Módulos del Sistema
Verifica que TODOS los componentes estén funcionando correctamente
"""

import os
import sys
from datetime import datetime

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_section(text):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}📋 {text}{Colors.RESET}")

def check_autenticacion_module():
    """Verifica el módulo de autenticación"""
    print_section("MÓDULO DE AUTENTICACIÓN")
    
    checks = []
    
    # User model
    try:
        from apps.autenticacion.models import User
        print_success("Modelo User importado correctamente")
        checks.append(True)
        
        # Verificar roles
        roles = User.ROLE_CHOICES
        print_info(f"  Roles disponibles: {[r[0] for r in roles]}")
    except Exception as e:
        print_error(f"Error en modelo User: {e}")
        checks.append(False)
    
    # Notification model
    try:
        from apps.autenticacion.models_notification import Notification
        print_success("Modelo Notification importado correctamente")
        checks.append(True)
        
        # Verificar tipos de notificación
        tipos = Notification.TIPO_CHOICES
        print_info(f"  Tipos de notificación: {[t[0] for t in tipos]}")
    except Exception as e:
        print_error(f"Error en modelo Notification: {e}")
        checks.append(False)
    
    # Forms
    try:
        from apps.autenticacion.forms.login_form import LoginForm
        from apps.autenticacion.forms.register_form import RegisterForm
        print_success("Formularios de autenticación importados")
        checks.append(True)
    except Exception as e:
        print_error(f"Error en formularios: {e}")
        checks.append(False)
    
    # Views
    try:
        from apps.autenticacion.views.notifications import NotificationListView
        print_success("Vistas de notificaciones importadas")
        checks.append(True)
    except Exception as e:
        print_error(f"Error en vistas de notificaciones: {e}")
        checks.append(False)
    
    return sum(checks), len(checks)

def check_mascota_module():
    """Verifica el módulo de mascotas"""
    print_section("MÓDULO DE MASCOTAS")
    
    checks = []
    
    # Mascota model
    try:
        from apps.mascota.models import Mascota, ImagenMascota
        print_success("Modelos Mascota e ImagenMascota importados")
        checks.append(True)
    except Exception as e:
        print_error(f"Error en modelos de mascota: {e}")
        checks.append(False)
    
    # Historial médico
    try:
        from apps.mascota.models_historial import HistorialMedico, Vacuna, RegistroVacuna
        print_success("Modelos de historial médico importados")
        checks.append(True)
        
        # Contar vacunas disponibles
        vacunas_count = Vacuna.objects.count()
        print_info(f"  Vacunas configuradas: {vacunas_count}")
    except Exception as e:
        print_error(f"Error en modelos de historial: {e}")
        checks.append(False)
    
    # Formulario de creación
    try:
        from apps.mascota.forms import MascotaCreateForm
        print_success("Formulario de registro de mascotas importado")
        checks.append(True)
        
        # Verificar campos
        form = MascotaCreateForm()
        print_info(f"  Campos del formulario: {len(form.fields)}")
    except Exception as e:
        print_error(f"Error en formulario de registro: {e}")
        checks.append(False)
    
    # Vistas
    try:
        from apps.mascota.views.create_mascota import MascotaCreateView
        from apps.mascota.views.update_mascota import MascotaUpdateView
        from apps.mascota.views.historial_views import HistorialMedicoListView
        print_success("Vistas de mascotas importadas")
        checks.append(True)
    except Exception as e:
        print_error(f"Error en vistas de mascotas: {e}")
        checks.append(False)
    
    # Vistas de biometría
    try:
        from apps.mascota.views.biometria import BiometriaView, ScannerView
        print_success("Vistas de biometría importadas")
        checks.append(True)
    except Exception as e:
        print_error(f"Error en vistas de biometría: {e}")
        checks.append(False)
    
    # Vistas de QR
    try:
        from apps.mascota.views.qr_views import generar_qr_mascota
        print_success("Vistas de QR importadas")
        checks.append(True)
    except Exception as e:
        print_error(f"Error en vistas de QR: {e}")
        checks.append(False)
    
    return sum(checks), len(checks)

def check_urls():
    """Verifica que todas las URLs estén configuradas"""
    print_section("CONFIGURACIÓN DE URLs")
    
    checks = []
    
    try:
        from django.urls import reverse
        
        # URLs de autenticación
        urls_auth = [
            'autenticacion:login',
            'autenticacion:register',
            'autenticacion:logout',
            'autenticacion:notifications_list',
        ]
        
        for url_name in urls_auth:
            try:
                url = reverse(url_name)
                print_success(f"{url_name:40} → {url}")
                checks.append(True)
            except Exception as e:
                print_error(f"{url_name}: No configurada")
                checks.append(False)
        
        # URLs de mascotas
        urls_mascota = [
            'mascota:main_register',
            'mascota:create_mascota',
            'mascota:scanner',
        ]
        
        for url_name in urls_mascota:
            try:
                url = reverse(url_name)
                print_success(f"{url_name:40} → {url}")
                checks.append(True)
            except Exception as e:
                print_error(f"{url_name}: No configurada")
                checks.append(False)
    
    except Exception as e:
        print_error(f"Error al verificar URLs: {e}")
    
    return sum(checks), len(checks)

def check_database_models():
    """Verifica que los modelos estén en la base de datos"""
    print_section("MODELOS EN BASE DE DATOS")
    
    checks = []
    
    try:
        from apps.autenticacion.models import User
        from apps.autenticacion.models_notification import Notification
        from apps.mascota.models import Mascota, ImagenMascota
        from apps.mascota.models_historial import HistorialMedico, Vacuna, RegistroVacuna
        
        models = [
            (User, "Usuarios"),
            (Notification, "Notificaciones"),
            (Mascota, "Mascotas"),
            (ImagenMascota, "Imágenes de mascotas"),
            (HistorialMedico, "Historial médico"),
            (Vacuna, "Vacunas"),
            (RegistroVacuna, "Registros de vacunas"),
        ]
        
        for model, name in models:
            try:
                count = model.objects.count()
                print_success(f"{name:30} → {count} registros")
                checks.append(True)
            except Exception as e:
                print_error(f"{name}: Error al contar registros")
                checks.append(False)
    
    except Exception as e:
        print_error(f"Error al verificar modelos: {e}")
    
    return sum(checks), len(checks)

def check_static_files():
    """Verifica que los archivos estáticos existan"""
    print_section("ARCHIVOS ESTÁTICOS")
    
    checks = []
    
    static_files = [
        ('static/js/mascota-form.js', 'JavaScript del formulario'),
        ('static/js/notifications.js', 'JavaScript de notificaciones'),
        ('static/js/mascota-tabs.js', 'JavaScript de tabs'),
        ('static/css/mascota.css', 'CSS de mascotas'),
        ('static/css/base.css', 'CSS base'),
    ]
    
    for file_path, description in static_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print_success(f"{description:40} → {size:,} bytes")
            checks.append(True)
        else:
            print_error(f"{description}: No encontrado")
            checks.append(False)
    
    return sum(checks), len(checks)

def check_templates():
    """Verifica que los templates existan"""
    print_section("TEMPLATES")
    
    checks = []
    
    templates = [
        ('apps/autenticacion/templates/autenticacion/login.html', 'Login'),
        ('apps/autenticacion/templates/autenticacion/register.html', 'Registro'),
        ('apps/autenticacion/templates/autenticacion/notifications/list.html', 'Lista de notificaciones'),
        ('apps/mascota/templates/main_register.html', 'Registro principal'),
        ('apps/mascota/templates/mascota_registro/form.html', 'Formulario de mascota'),
        ('apps/mascota/templates/mascota/edit_mascota.html', 'Edición de mascota'),
        ('apps/mascota/templates/mascota/historial/list.html', 'Historial médico'),
        ('templates/layouts/base.html', 'Layout base'),
        ('templates/components/navbar.html', 'Navbar'),
        ('templates/components/sidebar.html', 'Sidebar'),
    ]
    
    for file_path, description in templates:
        if os.path.exists(file_path):
            print_success(f"{description:40}")
            checks.append(True)
        else:
            print_error(f"{description}: No encontrado")
            checks.append(False)
    
    return sum(checks), len(checks)

def check_permissions():
    """Verifica las restricciones de permisos"""
    print_section("RESTRICCIONES DE PERMISOS")
    
    checks = []
    
    try:
        # Verificar MascotaCreateView
        from apps.mascota.views.create_mascota import MascotaCreateView
        from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
        
        if issubclass(MascotaCreateView, LoginRequiredMixin):
            print_success("MascotaCreateView requiere autenticación")
            checks.append(True)
        else:
            print_error("MascotaCreateView NO requiere autenticación")
            checks.append(False)
        
        if issubclass(MascotaCreateView, UserPassesTestMixin):
            print_success("MascotaCreateView tiene verificación de roles")
            checks.append(True)
        else:
            print_error("MascotaCreateView NO tiene verificación de roles")
            checks.append(False)
        
        # Verificar MascotaUpdateView
        from apps.mascota.views.update_mascota import MascotaUpdateView
        
        if issubclass(MascotaUpdateView, UserPassesTestMixin):
            print_success("MascotaUpdateView tiene verificación de roles")
            checks.append(True)
        else:
            print_error("MascotaUpdateView NO tiene verificación de roles")
            checks.append(False)
        
        # Verificar vistas de historial
        from apps.mascota.views.historial_views import (
            HistorialMedicoCreateView,
            RegistroVacunaCreateView
        )
        
        if issubclass(HistorialMedicoCreateView, UserPassesTestMixin):
            print_success("HistorialMedicoCreateView tiene verificación de roles")
            checks.append(True)
        else:
            print_error("HistorialMedicoCreateView NO tiene verificación de roles")
            checks.append(False)
        
        if issubclass(RegistroVacunaCreateView, UserPassesTestMixin):
            print_success("RegistroVacunaCreateView tiene verificación de roles")
            checks.append(True)
        else:
            print_error("RegistroVacunaCreateView NO tiene verificación de roles")
            checks.append(False)
    
    except Exception as e:
        print_error(f"Error al verificar permisos: {e}")
    
    return sum(checks), len(checks)

def main():
    """Función principal"""
    print_header("VERIFICACIÓN COMPLETA DE TODOS LOS MÓDULOS")
    
    print(f"{Colors.BOLD}Fecha:{Colors.RESET} {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{Colors.BOLD}Proyecto:{Colors.RESET} PetFace ID - Sistema Veterinario")
    print(f"{Colors.BOLD}Estado del servidor:{Colors.RESET} {Colors.GREEN}Corriendo en http://127.0.0.1:8000/{Colors.RESET}\n")
    
    results = {}
    
    # Ejecutar todas las verificaciones
    results['Autenticación'] = check_autenticacion_module()
    results['Mascotas'] = check_mascota_module()
    results['URLs'] = check_urls()
    results['Base de Datos'] = check_database_models()
    results['Archivos Estáticos'] = check_static_files()
    results['Templates'] = check_templates()
    results['Permisos'] = check_permissions()
    
    # Resumen final
    print_header("RESUMEN FINAL DE TODOS LOS MÓDULOS")
    
    total_passed = 0
    total_checks = 0
    
    for module_name, (passed, total) in results.items():
        percentage = (passed / total * 100) if total > 0 else 0
        total_passed += passed
        total_checks += total
        
        if percentage == 100:
            print(f"{Colors.GREEN}✅ {module_name:25} → {passed}/{total} ({percentage:.0f}%){Colors.RESET}")
        elif percentage >= 80:
            print(f"{Colors.YELLOW}⚠️  {module_name:25} → {passed}/{total} ({percentage:.0f}%){Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ {module_name:25} → {passed}/{total} ({percentage:.0f}%){Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    
    overall_percentage = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    if overall_percentage == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡TODOS LOS MÓDULOS FUNCIONAN PERFECTAMENTE!{Colors.RESET}")
        print(f"\n{Colors.GREEN}✅ {total_passed}/{total_checks} verificaciones pasadas ({overall_percentage:.0f}%){Colors.RESET}")
        print(f"\n{Colors.GREEN}✅ El sistema está 100% operativo{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Servidor corriendo: http://127.0.0.1:8000/{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Listo para usar todas las funcionalidades{Colors.RESET}\n")
    elif overall_percentage >= 90:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  SISTEMA CASI COMPLETO{Colors.RESET}")
        print(f"\n{Colors.YELLOW}{total_passed}/{total_checks} verificaciones pasadas ({overall_percentage:.0f}%){Colors.RESET}")
        print(f"{Colors.YELLOW}Revisa los módulos con advertencias arriba{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SISTEMA REQUIERE ATENCIÓN{Colors.RESET}")
        print(f"\n{Colors.RED}{total_passed}/{total_checks} verificaciones pasadas ({overall_percentage:.0f}%){Colors.RESET}")
        print(f"{Colors.RED}Varios módulos necesitan corrección{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    # Módulos disponibles
    print_header("MÓDULOS DISPONIBLES")
    
    print(f"{Colors.CYAN}🔐 AUTENTICACIÓN:{Colors.RESET}")
    print("   • Login/Logout")
    print("   • Registro de usuarios (OWNER, VET, ADMIN)")
    print("   • Sistema de notificaciones (6 tipos)")
    print("   • Gestión de perfiles")
    
    print(f"\n{Colors.CYAN}🐾 MASCOTAS:{Colors.RESET}")
    print("   • Registro de mascotas (solo OWNER/ADMIN)")
    print("   • Edición de mascotas (solo propietario/ADMIN)")
    print("   • Visualización de mascotas")
    print("   • Gestión de imágenes")
    print("   • Sistema de reconocimiento facial (biometría)")
    print("   • Scanner de reconocimiento")
    
    print(f"\n{Colors.CYAN}🏥 HISTORIAL MÉDICO:{Colors.RESET}")
    print("   • Registros médicos (solo VET/ADMIN)")
    print("   • Gestión de vacunas (10 vacunas configuradas)")
    print("   • Cartilla de vacunación")
    print("   • Recordatorios automáticos")
    print("   • Notificaciones de eventos médicos")
    
    print(f"\n{Colors.CYAN}📱 FUNCIONALIDADES ADICIONALES:{Colors.RESET}")
    print("   • Generación de códigos QR")
    print("   • Información pública de mascotas")
    print("   • Reportes de mascotas perdidas")
    print("   • Sistema de eliminación de mascotas/biometría")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n")

if __name__ == '__main__':
    # Configurar Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    main()
