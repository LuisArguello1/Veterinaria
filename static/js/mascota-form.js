/**
 * Validaciones y mejoras para el formulario de registro de mascotas
 * Solo para usuarios con rol OWNER y ADMIN
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mascota-form');
    
    if (!form) return;
    
    // Validación en tiempo real del nombre
    const nombreInput = form.querySelector('input[name="nombre"]');
    if (nombreInput) {
        nombreInput.addEventListener('input', function() {
            const value = this.value.trim();
            const errorContainer = this.parentElement.querySelector('.text-red-600');
            
            if (value.length === 0) {
                this.classList.add('border-red-300');
                this.classList.remove('border-green-300');
            } else if (value.length < 2) {
                this.classList.add('border-yellow-300');
                this.classList.remove('border-green-300', 'border-red-300');
            } else {
                this.classList.add('border-green-300');
                this.classList.remove('border-yellow-300', 'border-red-300');
            }
        });
    }
    
    // Validación en tiempo real del peso
    const pesoInput = form.querySelector('input[name="peso"]');
    if (pesoInput) {
        pesoInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            
            if (isNaN(value)) {
                this.classList.remove('border-green-300', 'border-red-300');
                return;
            }
            
            if (value < 0 || value > 500) {
                this.classList.add('border-red-300');
                this.classList.remove('border-green-300');
            } else {
                this.classList.add('border-green-300');
                this.classList.remove('border-red-300');
            }
        });
    }
    
    // Validación del formulario antes de enviar
    form.addEventListener('submit', function(e) {
        const nombre = nombreInput ? nombreInput.value.trim() : '';
        
        if (nombre.length < 2) {
            e.preventDefault();
            
            // Scroll hasta el campo de nombre
            nombreInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            nombreInput.focus();
            
            // Mostrar mensaje de error
            showNotification('Por favor, ingrese un nombre válido para la mascota (mínimo 2 caracteres).', 'error');
            
            return false;
        }
        
        // Mostrar indicador de carga
        showLoadingIndicator();
    });
    
    // Calcular edad aproximada desde fecha de nacimiento
    const fechaNacInput = form.querySelector('input[name="fecha_nacimiento"]');
    if (fechaNacInput) {
        fechaNacInput.addEventListener('change', function() {
            const fechaNac = new Date(this.value);
            const hoy = new Date();
            
            if (fechaNac > hoy) {
                showNotification('La fecha de nacimiento no puede ser futura.', 'warning');
                this.value = '';
                return;
            }
            
            const diffTime = Math.abs(hoy - fechaNac);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const diffMonths = Math.floor(diffDays / 30);
            const diffYears = Math.floor(diffMonths / 12);
            
            let edadTexto = '';
            if (diffYears > 0) {
                edadTexto = `${diffYears} año${diffYears > 1 ? 's' : ''}`;
                if (diffMonths % 12 > 0) {
                    edadTexto += ` y ${diffMonths % 12} mes${diffMonths % 12 > 1 ? 'es' : ''}`;
                }
            } else if (diffMonths > 0) {
                edadTexto = `${diffMonths} mes${diffMonths > 1 ? 'es' : ''}`;
            } else {
                edadTexto = `${diffDays} día${diffDays > 1 ? 's' : ''}`;
            }
            
            showNotification(`Edad aproximada: ${edadTexto}`, 'info');
            
            // Sugerir etapa de vida
            const etapaVidaSelect = form.querySelector('select[name="etapa_vida"]');
            if (etapaVidaSelect && !etapaVidaSelect.value) {
                let etapaSugerida = '';
                
                if (diffMonths < 12) {
                    etapaSugerida = 'cachorro';
                } else if (diffYears >= 1 && diffYears < 3) {
                    etapaSugerida = 'joven';
                } else if (diffYears >= 3 && diffYears < 7) {
                    etapaSugerida = 'adulto';
                } else if (diffYears >= 7) {
                    etapaSugerida = 'senior';
                }
                
                if (etapaSugerida) {
                    etapaVidaSelect.value = etapaSugerida;
                    etapaVidaSelect.classList.add('border-blue-300');
                    setTimeout(() => {
                        etapaVidaSelect.classList.remove('border-blue-300');
                    }, 2000);
                }
            }
        });
    }
});

/**
 * Mostrar indicador de carga durante el envío del formulario
 */
function showLoadingIndicator() {
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="pi pi-spin pi-spinner mr-2"></i> Registrando...';
        submitButton.classList.add('opacity-75', 'cursor-not-allowed');
    }
}

/**
 * Mostrar notificación temporal
 */
function showNotification(message, type = 'info') {
    const colors = {
        info: 'bg-blue-50 border-blue-400 text-blue-700',
        success: 'bg-green-50 border-green-400 text-green-700',
        warning: 'bg-yellow-50 border-yellow-400 text-yellow-700',
        error: 'bg-red-50 border-red-400 text-red-700'
    };
    
    const icons = {
        info: 'pi-info-circle',
        success: 'pi-check-circle',
        warning: 'pi-exclamation-triangle',
        error: 'pi-times-circle'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 ${colors[type]} border-l-4 p-4 rounded-md shadow-lg z-50 animate-slideInRight max-w-md`;
    notification.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <i class="pi ${icons[type]} text-xl"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto flex-shrink-0">
                <i class="pi pi-times text-sm"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Limpiar formulario con confirmación
 */
function resetForm() {
    if (confirm('¿Está seguro de que desea limpiar el formulario? Se perderán todos los datos ingresados.')) {
        const form = document.getElementById('mascota-form');
        if (form) {
            form.reset();
            
            // Limpiar vista previa de imagen
            const fotoPreview = document.getElementById('foto-preview');
            if (fotoPreview) {
                fotoPreview.classList.add('hidden');
            }
            
            // Limpiar clases de validación
            form.querySelectorAll('input, select, textarea').forEach(field => {
                field.classList.remove('border-green-300', 'border-red-300', 'border-yellow-300');
            });
            
            showNotification('Formulario limpiado correctamente.', 'success');
        }
    }
}

// Animaciones CSS adicionales
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    .animate-slideInRight {
        animation: slideInRight 0.3s ease-out;
    }
`;
document.head.appendChild(style);
