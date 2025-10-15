"""
Configuración de Django para el proyecto config.

Generado por 'django-admin startproject' usando Django 5.2.4.

Para más información sobre este archivo, ver
https://docs.djangoproject.com/en/5.2/topics/settings/

Para la lista completa de configuraciones y sus valores, ver
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import environ
import os
#Actualizacion de dependencias del proyecto
# SOLO EJECUTAR CUANDO SE VAYA ACTUALIZAR O CREAR LAS DEPENDENCIAS
# pip freeze > requirements.txt

# Construye rutas dentro del proyecto como esta: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#Variables de entorno
env = environ.Env(
    # establecer el tipo de conversión y el valor por defecto
    DEBUG=(bool, False)
)

# Tomar variables de entorno del archivo .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Configuración rápida para desarrollo - no apta para producción
# Ver https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# ADVERTENCIA DE SEGURIDAD: ¡mantén la clave secreta usada en producción en secreto!
SECRET_KEY = env('SECRET_KEY')

# ADVERTENCIA DE SEGURIDAD: ¡no ejecutes con debug activado en producción!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = []

# Definición de aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Aplicaciones de terceros
THIRD_PARTY_APPS = [
    'django_extensions',
    'widget_tweaks',
    'tailwind',
    'theme',
]

# Aplicaciones locales
LOCAL_APPS = [
    'apps.autenticacion',
    'apps.mascota'
]

# Apps solo para DEBUG, y no para produccion
if DEBUG:
    THIRD_PARTY_APPS += ['django_browser_reload']

INSTALLED_APPS = INSTALLED_APPS + THIRD_PARTY_APPS + LOCAL_APPS

TAILWIND_APP_NAME = 'theme'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Middleware solo para DEBUG, y no para produccion
if DEBUG:
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# Validación de contraseñas
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internacionalización
# https://docs.djangoproject.com/en/5.2/topics/i18n/
#Idioma: Español, Pais: Ecuador
LANGUAGE_CODE = 'es-ec'

TIME_ZONE = 'America/Guayaquil'

USE_I18N = True

USE_TZ = True

#Para Produccion
# SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
# SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
# CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")

# Archivos estáticos (CSS, JavaScript, Imágenes)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Configuración de archivos de estaticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static",]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración de archivos de medios
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de cache para archivos estáticos y media
STATIC_FILE_MAX_AGE = 60 * 60 * 24 * 30  # 30 días en segundos
MEDIA_FILE_MAX_AGE = 60 * 60 * 24 * 7    # 7 días en segundos

#Npm configuracion para Tailwin
NPM_BIN_PATH = r"D:\Node Js\npm.cmd"

# Tipo de campo de clave primaria por defecto
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

AUTH_USER_MODEL = 'autenticacion.User'

# Configuración de autenticación personalizada
AUTHENTICATION_BACKENDS = [
    'apps.autenticacion.backends.EmailBackend',  
    'django.contrib.auth.backends.ModelBackend',  
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'auth:Dashboard'  
LOGOUT_REDIRECT_URL = 'auth:login'    

# Configuracion de guardado de la imagenes y videos en azure
# STORAGES = {
#     "default": {
#         "BACKEND": "storages.backends.azure_storage.AzureStorage",
#         "OPTIONS": {
#             'timeout': 20,
#             'expiration_secs':500,
#         },
#     },
#     "staticfiles": {
#         "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#     },
# }

#Variables de entorno para azure
# AZURE_CONTAINER=env('AZURE_CONTAINER')
# AZURE_ACCOUNT_NAME=env('AZURE_ACCOUNT_NAME')
# AZURE_ACCOUNT_KEY=env('AZURE_ACCOUNT_KEY')

#Configuración de envío de correos
# Para producción (descomentar y configurar en .env)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

# Configuración de límites de carga para imágenes biométricas
# Aumentar límites para permitir imágenes de alta resolución desde cámaras
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB (por defecto es 2.5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB (por defecto es 2.5MB)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # Por defecto es 1000
