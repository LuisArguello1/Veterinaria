/**
 * Utilities Module
 * Funciones de utilidad general para toda la aplicación
 */

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'info', duration = 3000) {
    const icons = {
        success: 'success',
        error: 'error',
        warning: 'warning',
        info: 'info'
    };

    Swal.fire({
        text: message,
        icon: icons[type] || 'info',
        timer: duration,
        showConfirmButton: false,
        toast: true,
        position: 'top-end',
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    });
}

// Función para validar formularios
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;
    let errors = [];

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            errors.push(`El campo ${field.getAttribute('data-label') || field.name} es requerido`);
            field.classList.add('border-red-500');
        } else {
            field.classList.remove('border-red-500');
        }
    });

    if (!isValid) {
        showToast(errors[0], 'error');
    }

    return isValid;
}

// Función para formatear fechas
function formatDate(dateString, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    const finalOptions = { ...defaultOptions, ...options };
    const date = new Date(dateString);
    
    return date.toLocaleDateString('es-ES', finalOptions);
}

// Función para debounce (evitar múltiples llamadas rápidas)
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}