import secrets
import os
from datetime import datetime

# Variables requeridas con valores por defecto organizadas por secciones
REQUIRED_VARS = {
    'DJANGO': {
        'SECRET_KEY': lambda: secrets.token_urlsafe(50), 
        'DEBUG': 'True',
        'BASE_URL': 'http://localhost:8000',
    },
    'DATABASE': {
        'DB_NAME': 'veterinaria',
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'tu_password_db',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
    },
    'AZURE_STORAGE': {
        'AZURE_ACCOUNT_NAME': 'tu_account_azure',
        'AZURE_ACCOUNT_KEY': 'tu_key_azure',
        'AZURE_CONTAINER': 'media',
    },
    'EMAIL': {
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': '587',
        'EMAIL_HOST_USER': 'tu_correo',
        'EMAIL_HOST_PASSWORD': 'tu_contraseña',
        'EMAIL_USE_TLS': 'True',
        'DEFAULT_FROM_EMAIL': 'tu_correo',
    },
    'SECURITY': {
        'SECURE_SSL_REDIRECT': 'False',
        'SESSION_COOKIE_SECURE': 'False',
        'CSRF_COOKIE_SECURE': 'False',
    },
    'CHATBOT': {
        'CHATBOT_IDENTITY_SECRET': 'tu_api_chatbot',
        'DJANGO_SETTINGS_MODULE': 'config.settings',
    },
    'MAPBOX': {
        'MAPBOX_TOKEN': 'tu_token_mapbox',
    },
}

ENV_FILE = '.env'
BACKUP_FOLDER = '.env_backups'


def parse_env_file(content):
    """
    Parsea el contenido del archivo .env y devuelve un diccionario con las variables.
    Mantiene comentarios y líneas vacías en una lista separada.
    """
    variables = {}
    lines_info = []  # Lista de tuplas (tipo, contenido, línea_número)
    
    for idx, line in enumerate(content.split('\n'), 1):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#'):
            lines_info.append(('comment', line, idx))
        elif '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            variables[key] = value
            lines_info.append(('variable', (key, value), idx))
        else:
            lines_info.append(('other', line, idx))
    
    return variables, lines_info


def create_backup():
    """Crea un backup del archivo .env existente"""
    if not os.path.exists(ENV_FILE):
        return None
    
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_FOLDER, f'.env.backup_{timestamp}')
    
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return backup_file


def generate_env_content(existing_vars=None):
    """
    Genera el contenido del archivo .env con todas las variables requeridas.
    Si existing_vars se proporciona, mantiene los valores existentes.
    """
    content = f"# Variables de entorno - Generado/Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for section, variables in REQUIRED_VARS.items():
        content += f"# {section.replace('_', ' ')}\n"
        
        for key, default_value in variables.items():
            # Si la variable ya existe, mantener su valor
            if existing_vars and key in existing_vars:
                value = existing_vars[key]
            else:
                # Si es una función lambda (como SECRET_KEY), ejecutarla
                if callable(default_value):
                    value = default_value()
                else:
                    value = default_value
            
            content += f"{key}={value}\n"
        
        content += "\n"
    
    return content


def update_env_file():
    """
    Actualiza el archivo .env agregando variables faltantes y manteniendo las existentes.
    """
    if not os.path.exists(ENV_FILE):
        print("📝 Creando nuevo archivo .env...")
        content = generate_env_content()
        
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo .env creado exitosamente.")
        print("⚠️  Edita los valores placeholder con tu configuración real.")
        return
    
    # Leer archivo existente
    print("🔍 Verificando archivo .env existente...")
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    existing_vars, _ = parse_env_file(existing_content)
    
    # Verificar qué variables faltan
    all_required_vars = {}
    for section in REQUIRED_VARS.values():
        all_required_vars.update(section)
    
    missing_vars = []
    for key in all_required_vars.keys():
        if key not in existing_vars:
            missing_vars.append(key)
    
    if not missing_vars:
        print("✅ El archivo .env está actualizado. Todas las variables están presentes.")
        return
    
    # Crear backup antes de actualizar
    backup_file = create_backup()
    if backup_file:
        print(f"💾 Backup creado: {backup_file}")
    
    # Generar nuevo contenido manteniendo valores existentes
    print(f"📝 Actualizando .env con {len(missing_vars)} variable(s) faltante(s):")
    for var in missing_vars:
        print(f"   + {var}")
    
    new_content = generate_env_content(existing_vars)
    
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Archivo .env actualizado exitosamente.")
    print("⚠️  Revisa las nuevas variables y configura sus valores.")


def show_env_status():
    """Muestra el estado actual de las variables de entorno"""
    if not os.path.exists(ENV_FILE):
        print("❌ El archivo .env no existe.")
        return
    
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    existing_vars, _ = parse_env_file(content)
    
    # Recopilar todas las variables requeridas
    all_required_vars = {}
    for section in REQUIRED_VARS.values():
        all_required_vars.update(section)
    
    print("\n📊 Estado de las variables de entorno:")
    print("=" * 60)
    
    # Variables configuradas
    configured = []
    placeholders = []
    missing = []
    
    for key, default_value in all_required_vars.items():
        if key in existing_vars:
            value = existing_vars[key]
            # Verificar si es un placeholder
            if 'tu_' in value.lower() or value == (default_value if not callable(default_value) else ''):
                placeholders.append((key, value))
            else:
                configured.append((key, value))
        else:
            missing.append(key)
    
    if configured:
        print(f"\n✅ Configuradas ({len(configured)}):")
        for key, value in configured:
            # Ocultar valores sensibles
            if 'PASSWORD' in key or 'KEY' in key:
                display_value = '*' * 10
            else:
                display_value = value[:30] + '...' if len(value) > 30 else value
            print(f"   {key} = {display_value}")
    
    if placeholders:
        print(f"\n⚠️  Con valores placeholder ({len(placeholders)}):")
        for key, value in placeholders:
            print(f"   {key} = {value}")
    
    if missing:
        print(f"\n❌ Faltantes ({len(missing)}):")
        for key in missing:
            print(f"   {key}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--status':
        show_env_status()
    else:
        update_env_file()
        print("\n💡 Tip: Usa 'python create_env.py --status' para ver el estado de tu configuración.")