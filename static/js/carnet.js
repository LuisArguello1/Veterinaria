// static/js/carnet.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Módulo de carnet cargado');
    
    // Inicializar funcionalidades del módulo de carnet
    initCarnetModule();
});

function initCarnetModule() {
    // Agregar animaciones a las tarjetas
    addCardAnimations();
    
    // Configurar botones de descarga
    setupDownloadButtons();
    
    // Configurar vista previa de impresión
    setupPrintPreview();
    
    // Agregar tooltips informativos
    addTooltips();
    
    // Configurar lazy loading para imágenes
    setupLazyLoading();
}

/**
 * Agrega animaciones suaves a las tarjetas de carnet
 */
function addCardAnimations() {
    const cards = document.querySelectorAll('.carnet-card, .carnet-info-card');
    
    // Intersection Observer para animaciones al scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    cards.forEach(card => {
        observer.observe(card);
        
        // Efecto hover mejorado
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Configura los botones de descarga con feedback visual
 */
function setupDownloadButtons() {
    const downloadButtons = document.querySelectorAll('[href*="descargar_carnet_pdf"]');
    
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Agregar loading state
            const originalText = this.innerHTML;
            const originalClass = this.className;
            
            this.innerHTML = '<svg class="w-4 h-4 animate-spin inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>Generando PDF...';
            this.classList.add('opacity-75', 'cursor-not-allowed');
            this.style.pointerEvents = 'none';
            
            // Restaurar estado después de un tiempo
            setTimeout(() => {
                this.innerHTML = originalText;
                this.className = originalClass;
                this.style.pointerEvents = 'auto';
                
                // Mostrar mensaje de éxito
                showSuccessMessage('PDF descargado exitosamente');
            }, 3000);
        });
    });
}

/**
 * Configura la vista previa de impresión
 */
function setupPrintPreview() {
    const printButtons = document.querySelectorAll('[href*="vista_previa_carnet"]');
    
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Agregar parámetro para auto-print
            const url = new URL(this.href);
            url.searchParams.set('print', 'true');
            this.href = url.toString();
        });
    });
    
    // Configurar botón de imprimir en vista previa
    const printPageButton = document.querySelector('[onclick="window.print()"]');
    if (printPageButton) {
        printPageButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Preparar página para impresión
            document.body.classList.add('printing');
            
            // Imprimir
            window.print();
            
            // Limpiar clase después de imprimir
            setTimeout(() => {
                document.body.classList.remove('printing');
            }, 1000);
        });
    }
}

/**
 * Agrega tooltips informativos
 */
function addTooltips() {
    const elementsWithTooltip = [
        { selector: '.uuid-value', text: 'Código único de identificación para acceso público' },
        { selector: '.status-perdida', text: 'Esta mascota ha sido reportada como perdida' },
        { selector: '.status-casa', text: 'Esta mascota está en casa con su propietario' },
        { selector: '.status-entrenada', text: 'El reconocimiento biométrico está activo' },
        { selector: '.status-pendiente', text: 'Se necesitan más imágenes para el entrenamiento' }
    ];
    
    elementsWithTooltip.forEach(({ selector, text }) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.title = text;
            element.style.cursor = 'help';
        });
    });
}

/**
 * Configura lazy loading para imágenes
 */
function setupLazyLoading() {
    const images = document.querySelectorAll('img[src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Agregar efecto de fade in
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.3s ease';
                    
                    img.onload = function() {
                        this.style.opacity = '1';
                    };
                    
                    // Si la imagen ya está cargada
                    if (img.complete) {
                        img.style.opacity = '1';
                    }
                    
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
}

/**
 * Muestra mensaje de éxito
 */
function showSuccessMessage(message) {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300';
    notification.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            ${message}
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Mostrar animación
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(full)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * Funciones utilitarias para el módulo de carnet
 */
const CarnetUtils = {
    /**
     * Formatea un UUID para mejor legibilidad
     */
    formatUUID: function(uuid) {
        if (!uuid) return 'No asignado';
        return uuid.toString().toLowerCase();
    },
    
    /**
     * Crea un elemento de estado basado en el tipo
     */
    createStatusBadge: function(type, text) {
        const badge = document.createElement('span');
        badge.className = `status-badge status-${type}`;
        badge.textContent = text;
        return badge;
    },
    
    /**
     * Valida si una imagen existe
     */
    validateImage: function(imgElement) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = imgElement.src;
        });
    },
    
    /**
     * Genera un código QR (placeholder para implementación futura)
     */
    generateQRCode: function(uuid) {
        // Implementar cuando se agregue librería de QR
        console.log('Generar QR para UUID:', uuid);
    }
};

// Exponer funciones globalmente si es necesario
window.CarnetUtils = CarnetUtils;

// Manejo de errores para imágenes
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        // Reemplazar imagen rota con placeholder
        e.target.style.display = 'none';
        
        const placeholder = document.createElement('div');
        placeholder.className = 'w-full h-full flex items-center justify-center text-gray-400 bg-gray-200 rounded-full';
        placeholder.innerHTML = '<svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path></svg>';
        
        e.target.parentNode.appendChild(placeholder);
    }
}, true);

// Configuración de impresión específica
window.addEventListener('beforeprint', function() {
    document.body.classList.add('printing');
});

window.addEventListener('afterprint', function() {
    document.body.classList.remove('printing');
});

console.log('Módulo de carnet cargado completamente');