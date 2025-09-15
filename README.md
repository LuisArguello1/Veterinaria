# PET FACE ID - Sistema de Gestión Veterinaria

![PET FACE ID Logo](static/img/petfaceid_logo.png)

Sistema de gestión para clínicas veterinarias que permite administrar usuarios, mascotas, citas y más.

## 📋 Contenido

- [Instalación](#-instalación)
- [Características](#-características)
- [Cómo Colaborar](#-cómo-colaborar-en-el-proyecto)
- [Convenciones](#-convenciones)
- [Tecnologías](#-tecnologías)

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/LuisArguello1/Veterinaria.git
cd Veterinaria

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Realizar migraciones
python manage.py migrate

# Ejecutar servidor
python manage.py runserver

# Si instalas librerias extras, actualizar los requirements.txt
pip freeze > requirements.txt
```

## ✨ Características

- **Gestión de usuarios con roles**: Administradores, Veterinarios y Dueños de mascotas
- **Gestión de mascotas**
- **Interfaz moderna con diseño responsive**
- **Sistema de autenticación seguro**

## 📌 Cómo Colaborar en el Proyecto

### 🔹 1. Clonar el repositorio

Primero descarga el proyecto en tu máquina:

```bash
git clone https://github.com/LuisArguello1/Veterinaria.git
```

### 🔹 2. Actualizar cambios antes de trabajar

Siempre asegúrate de tener la última versión de master:

```bash
git checkout master
git pull origin master
```

### 🔹 3. Crear una nueva rama

Nunca trabajes directo en master.
Ejemplo si trabajas en el módulo de citas:

```bash
git checkout -b feature/citas
```

### 🔹 4. Guardar y subir tus cambios

Agrega tus cambios al repositorio:

```bash
git add .
git commit -m "feat: módulo de citas creado"
git push origin feature/citas
```

### 🔹 5. Crear un Pull Request (PR)

1. Ve a GitHub → aparecerá la opción **Compare & pull request**
2. Describe tus cambios claramente
3. Solicita el merge hacia master
4. El líder del proyecto revisará y aprobará el merge

## 📌 Convenciones

### Convenciones de Ramas

- `feature/nombre_funcionalidad` → nuevas funcionalidades
- `fix/nombre_bug` → correcciones de errores
- `hotfix/nombre_bug` → parches urgentes en producción

**Ejemplos:**
```bash
git checkout -b feature/gestion_mascotas
git checkout -b fix/bug_login
```

### Convenciones de Commits

Usar prefijos para claridad:

- `feat:` → nueva funcionalidad
- `fix:` → corrección de errores
- `refactor:` → mejora de código sin cambiar funcionalidad
- `style:` → cambios de diseño (HTML, CSS, JS)
- `docs:` → documentación

**Ejemplos:**
```bash
git commit -m "feat: gestión de usuarios con roles ADMIN, OWNER, VET"
git commit -m "fix: error en validación de cédula"
```

## 📌 Recomendaciones Rápidas

- **Antes de empezar** → `git pull origin master`
- **Trabaja siempre en tu propia rama**
- **Haz commits claros y descriptivos**
- **Sube tus cambios** → `git push origin tu_rama`
- **Crea un Pull Request en GitHub**
- **El líder revisa y hace el merge a master**


---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.

