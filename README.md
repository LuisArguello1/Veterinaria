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

---

## � Guía de Ejecución

Una vez completada la instalación, puedes ejecutar el proyecto de diferentes maneras según tus necesidades.

### **1. Ejecutar en Puerto Predeterminado (8000)**

Esta es la forma más común de ejecutar el servidor de desarrollo:

```bash
python manage.py runserver
```

**Acceder a la aplicación:**
- 🌐 **URL:** `http://127.0.0.1:8000/`
- 🔗 **También funciona:** `http://localhost:8000/`

**Salida esperada:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
November 06, 2025 - 10:30:00
Django version 5.2.6, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### **2. Ejecutar en Puerto Personalizado**

Si el puerto 8000 está ocupado o prefieres usar otro puerto:

```bash
python manage.py runserver 8080
```

> 🔢 Puedes usar cualquier puerto disponible: `3000`, `5000`, `8080`, `9000`, etc.

**Ejemplos de puertos alternativos:**

```bash
# Puerto 3000
python manage.py runserver 3000

# Puerto 5000
python manage.py runserver 5000

# Puerto 9000
python manage.py runserver 9000
```

**Acceder a la aplicación:**
- 🌐 **URL:** `http://127.0.0.1:[PUERTO]/`
- **Ejemplo:** `http://127.0.0.1:8080/`

---

### **4. Detener el Servidor**

Para detener el servidor de desarrollo:

- **Windows (CMD/PowerShell):** Presiona `CTRL + C`
- **Linux/Mac:** Presiona `CTRL + C`

Verás un mensaje similar a:
```
Quit the server with CTRL-C.
^C
```

---

### **Comandos Rápidos de Ejecución**

| Comando | Descripción | URL de Acceso |
|---------|-------------|---------------|
| `python manage.py runserver` | Puerto predeterminado (8000) | `http://127.0.0.1:8000/` |
| `python manage.py runserver 3000` | Puerto personalizado (3000) | `http://127.0.0.1:3000/` |

---

### **Consejos de Ejecución**

✅ **Antes de ejecutar el servidor:**
```bash
# 1. Activa el entorno virtual
cd venv\Scripts
activate

# 2. Verifica que no haya errores
python manage.py check

# 3. Aplica migraciones pendientes (si las hay)
python manage.py migrate

# 4. Ejecuta el servidor
python manage.py runserver
```


# 📖 Manual de Usuario

## 🚀 Acceso al Sistema

Accede a: `http://127.0.0.1:8000/`

**Opciones de inicio:**
- 🔑 Email y contraseña
- 👤 Reconocimiento facial (si está configurado)

**Credenciales admin:** `admin@gmail.com` / `admin123`

---

## 👥 Registro de Usuarios

1. Clic en **"Registrarse"**
2. Completa: Email, nombre, teléfono, dirección, contraseña
3. Confirma contraseña
4. **"Registrarse"** → Acceso al dashboard

**Opcional:** Configura reconocimiento facial desde tu perfil

---

## 🐾 Registrar Mascota

### Datos Requeridos

**Información básica:**
- Nombre (mínimo 2 caracteres)
- Raza
- Sexo: Macho/Hembra
- Etapa de vida: Cachorro/Adulto/Senior

**Datos físicos:**
- **Edad:** 0-30 (años o meses)
- **Peso:** 0.1-200 kg
- Color
- Estado corporal: Delgado/Normal/Sobrepeso/Obeso
- Fecha de nacimiento (debe coincidir con edad ±3 meses)

**Otros:**
- Características especiales (mínimo 5 caracteres)
- Foto de perfil (requerida, máx 5MB)

### Validaciones Automáticas

Al presionar **"Guardar"**, el sistema valida:

✅ **Edad válida (0-30):**
- ❌ Error: `⚠️ La edad debe estar entre 0 y 30 (ingresaste: 122)`

✅ **Peso válido (0.1-200 kg):**
- ❌ Error: `⚠️ El peso debe estar entre 0.1 kg y 200 kg (ingresaste: 12333 kg)`

✅ **Coherencia edad/fecha (±3 meses):**
- ❌ Error: `⚠️ La edad (12 años) no coincide con la fecha de nacimiento (1 año y 0 meses)`

**Los campos con error muestran borde rojo y mensaje específico debajo**

---

## ✏️ Editar Mascota

1. Clic en ✏️ **"Editar"** en la mascota
2. Modifica los datos necesarios
3. **"Guardar Cambios"** → Valida automáticamente
4. Corrige errores (si hay) y guarda nuevamente

---

## 🎯 Reconocimiento Facial

### Configurar Biometría

1. Accede a detalles de mascota
2. **"Registrar Biometría"**
3. Sube **15-20 fotos** de diferentes ángulos:
   - Frontal, lateral izquierdo, lateral derecho
   - Buena iluminación, fondo uniforme
   - Mascota tranquila
4. **"Procesar y Guardar"**

### Usar Escáner

1. **"Escáner Facial"** desde menú
2. Toma/sube foto de la mascota
3. Sistema identifica y muestra información
4. Contacta propietario si es necesario

---

## 🎨 Funcionalidades Extra

- 📄 **Generar carnet** con QR code
- 🔍 **Buscar mascotas** por nombre, raza, color
- 📊 **Dashboard** con estadísticas
- 🔔 **Notificaciones** automáticas

---

## 💡 Consejos Importantes

### ✅ Hacer:
- Fotos claras y bien iluminadas
- Datos precisos (peso real, edad correcta)
- 15-20 fotos para biometría

### ❌ Evitar:
- Valores extremos: peso 0 o 12333, edad negativa
- Imágenes >5MB
- Menos de 15 fotos biométricas

---

## 🆘 Errores Comunes

| Error | Solución |
|-------|----------|
| Edad/fecha no coinciden | Verifica que la edad y fecha sean coherentes (±3 meses) |
| Peso inválido | Ingresa peso entre 0.1 y 200 kg |
| Imagen muy grande | Comprime foto a menos de 5MB |
| Pocas imágenes biométricas | Sube al menos 15 fotos |

---

**Soporte:** Contacta al administrador del sistema  
**Versión:** 1.0 | **Actualizado:** Noviembre 2025
