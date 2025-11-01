# Guía de Instalación - PET FACE ID

> Sistema de Gestión Veterinaria con Reconocimiento Facial de Mascotas

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

| Software | Versión Mínima | Enlace de Descarga |
|----------|----------------|-------------------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **PostgreSQL** | 14+ | [postgresql.org](https://www.postgresql.org/download/) |
| **Git** | 2.0+ | [git-scm.com](https://git-scm.com/downloads) |

### Verificar Instalaciones

```bash
python --version
psql --version
git --version
```

---

## Instalación Paso a Paso

### **Paso 1:** Clonar el Repositorio

```bash
git clone https://github.com/LuisArguello1/Veterinaria.git
```
```bash
cd Veterinaria
```


---

### **Paso 2:** Crear y Activar el Entorno Virtual

#### En Windows (CMD):
```cmd
python -m venv venv
```
```cmd
cd venv/scripts
```
```cmd
activate
```

#### En Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 **Nota:** Verás `(venv)` al inicio de tu terminal cuando esté activado correctamente.

---

### **Paso 3:** Instalar Dependencias

Con el entorno virtual activado, instala todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- Django 5.2.6 (Framework web)
- psycopg2 (Conexión PostgreSQL)
- OpenCV (Reconocimiento facial)
- Django Tailwind (Estilos CSS)
- Pillow, NumPy (Procesamiento de imágenes)

Este proceso puede tomar algunos minutos...

---

### **Paso 4:** Configurar la Base de Datos

El proyecto utiliza PostgreSQL y las credenciales se encuentran en el archivo `.env` que está incluido en el repositorio.

#### Verificar archivo `.env`

Asegúrate de que el archivo `.env` en la raíz del proyecto contenga las siguientes variables:

```env
# Django Settings
SECRET_KEY=tu-clave-secreta
DEBUG=True

# Database Configuration
DB_NAME=nombre_de_tu_base_de_datos
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

#### 🗄️ Crear la Base de Datos en PostgreSQL

Abre **pgAdmin** y crea una nueva base de datos 

> ⚠️ **Importante:** El nombre de la base de datos debe coincidir con `DB_NAME` en tu archivo `.env`
---

### **Paso 5:** Realizar las Migraciones

Genera y aplica las migraciones para crear las tablas en la base de datos:

```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```

**Salida esperada:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying autenticacion.0001_initial... OK
  Applying mascota.0001_initial... OK
  ...
```

---

### **Paso 6:** Crear el Superusuario

Ejecuta el script personalizado para crear el superusuario:

```bash
python createsuperuser.py
```

**Credenciales por defecto:**
- 👤 **Usuario:** Admin
- 📧 **Email:** admin@gmail.com
- 🔑 **Contraseña:** admin123

> 💡 **Nota:** Si el usuario ya existe, el script te mostrará la información actual sin crear uno nuevo.

---

### **Paso 7:** Verificar el Proyecto

Ejecuta el siguiente comando para verificar que no hay errores de configuración:

```bash
python manage.py check
```

**Salida esperada:**
```
System check identified no issues (0 silenced).
```

✅ Si ves este mensaje, ¡todo está configurado correctamente!

---

### **Paso 8:** Ejecutar el Servidor de Desarrollo

Inicia el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

**Salida esperada:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
November 01, 2025 - 10:30:00
Django version 5.2.6, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🌐 Acceder al Sistema

### Aplicación Principal
```
http://127.0.0.1:8000/
```

### Panel de Administración
```
http://127.0.0.1:8000/admin/
```
- **Email:** admin@gmail.com
- **Contraseña:** admin123

---

## 📝 Resumen de Comandos

Para referencia rápida, aquí están todos los comandos en secuencia:

```bash
# 1. Clonar repositorio
git clone https://github.com/LuisArguello1/Veterinaria.git
cd Veterinaria

# 2. Crear y activar entorno virtual
python -m venv venv
cd venv/scripts
activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env (verificar que exista y esté configurado)

# 5. Realizar migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Crear superusuario
python createsuperuser.py

# 7. Verificar proyecto
python manage.py check

# 8. Ejecutar servidor
python manage.py runserver
```

---

## ❓ Solución de Problemas Comunes

### 🔴 Error: "No module named 'django'"

**Causa:** El entorno virtual no está activado o las dependencias no se instalaron.

**Solución:**
```bash
cd venv\Scripts
activate

pip install -r requirements.txt
```

---

### 🔴 Error de conexión a PostgreSQL

**Causa:** PostgreSQL no está corriendo o las credenciales en `.env` son incorrectas.
Verifica que el nombre de la base de datos en el archivo `.env` sea igual a la base de datos que creaste en pgadmin.


### 🔴 Error: "SECRET_KEY not found"

**Causa:** El archivo `.env` no existe o no contiene la variable SECRET_KEY.

**Solución:** Verifica que el archivo `.env` esté en la raíz del proyecto con todas las variables necesarias.

---

### 🔴 Error: "El usuario 'admin' ya existe"

**Causa:** Ya ejecutaste el script `createsuperuser.py` anteriormente.

**Solución:** Este no es un error, el script simplemente te informa que el usuario ya existe. Puedes usar las credenciales existentes para iniciar sesión.
---
## 👥 Soporte

Si encuentras algún problema durante la instalación:

1. Revisa la sección **Solución de Problemas Comunes**
2. Verifica que todos los requisitos previos estén instalados
3. Consulta con el equipo de desarrollo del proyecto

---

## ⚠️ Notas Importantes

- ✅ El archivo `.env` está incluido en el repositorio (para desarrollo)
- ✅ Asegúrate de tener PostgreSQL corriendo antes de las migraciones
- ✅ Usa `python createsuperuser.py` en lugar de `manage.py createsuperuser`
- ✅ Ejecuta `python manage.py check` antes de iniciar el servidor
- ✅ Los modelos de IA están en la carpeta `/models/`

---

**¡Listo! Ahora puedes comenzar a trabajar con PET FACE ID**
