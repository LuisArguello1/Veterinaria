/**
 * JavaScript para la página de información pública de mascotas
 * Funcionalidades específicas para la vista pública del QR
 */

/**
 * Inicializa la página de información pública
 */
function initPublicInfoPage() {
    console.log('Inicializando página de información pública');
    
    // Detectar dispositivo móvil
    detectMobileDevice();
    
    // Configurar enlaces de contacto
    setupContactLinks();
    
    // Configurar funcionalidades adicionales
    setupAdditionalFeatures();
}

/**
 * Detecta si es un dispositivo móvil y aplica optimizaciones
 */
function detectMobileDevice() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        document.body.classList.add('mobile-device');
        console.log('Dispositivo móvil detectado - optimizaciones aplicadas');
    }
}

/**
 * Configura los enlaces de contacto para mejor funcionamiento en móviles
 */
function setupContactLinks() {
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    
    // Configurar enlaces de email
    emailLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // El comportamiento por defecto ya maneja mailto: correctamente
            console.log('Enlace de email activado:', this.href);
        });
        
        // Agregar título descriptivo para accesibilidad
        if (!link.title) {
            link.title = 'Enviar email al propietario';
        }
    });
    
    // Configurar enlaces de teléfono
    phoneLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // El comportamiento por defecto ya maneja tel: correctamente
            console.log('Enlace de teléfono activado:', this.href);
        });
        
        // Agregar título descriptivo para accesibilidad
        if (!link.title) {
            link.title = 'Llamar al propietario';
        }
    });
    
    if (emailLinks.length > 0 || phoneLinks.length > 0) {
        console.log(`Enlaces de contacto configurados: ${emailLinks.length} emails, ${phoneLinks.length} teléfonos`);
    }
}

/**
 * Configura funcionalidades adicionales de la página
 */
function setupAdditionalFeatures() {
    // Mejorar la experiencia visual en imágenes
    setupImageEnhancements();
    
    // Configurar accesibilidad mejorada
    setupAccessibilityFeatures();
    
    // Configurar animaciones sutiles
    setupAnimations();
}

/**
 * Mejora la experiencia con las imágenes
 */
function setupImageEnhancements() {
    const petImages = document.querySelectorAll('.pet-avatar, img[alt*="Foto de"]');
    
    petImages.forEach(img => {
        // Agregar efecto de carga
        img.addEventListener('load', function() {
            this.style.opacity = '0';
            this.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 50);
        });
        
        // Manejar errores de carga
        img.addEventListener('error', function() {
            console.log('Error cargando imagen:', this.src);
            // La imagen ya tiene fallbacks definidos en el HTML
        });
    });
}

/**
 * Mejora las características de accesibilidad
 */
function setupAccessibilityFeatures() {
    // Mejorar navegación por teclado
    const interactiveElements = document.querySelectorAll('a, button');
    
    interactiveElements.forEach(element => {
        // Agregar indicador visual de foco si no existe
        element.addEventListener('focus', function() {
            if (!this.style.outline) {
                this.style.outline = '2px solid #1d4ed8';
                this.style.outlineOffset = '2px';
            }
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
}

/**
 * Configura animaciones sutiles para mejorar la experiencia
 */
function setupAnimations() {
    // Animación de entrada para las tarjetas
    const cards = document.querySelectorAll('.bg-white');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

/**
 * Funciones de utilidad para la página pública
 */
window.publicInfoUtils = {
    /**
     * Refresca la información de la página
     */
    refresh: function() {
        location.reload();
    },
    
    /**
     * Comparte la información de la mascota (si el navegador lo soporta)
     * @param {string} mascotaNombre - Nombre de la mascota
     * @param {string} currentUrl - URL actual
     */
    share: async function(mascotaNombre, currentUrl) {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: `Información de ${mascotaNombre} - PetFaceID`,
                    text: `Información de la mascota ${mascotaNombre}`,
                    url: currentUrl
                });
                console.log('Información compartida exitosamente');
            } catch (error) {
                console.log('Error compartiendo:', error);
                this.fallbackShare(currentUrl);
            }
        } else {
            this.fallbackShare(currentUrl);
        }
    },
    
    /**
     * Método alternativo de compartir si el navegador no soporta Web Share API
     * @param {string} url - URL a compartir
     */
    fallbackShare: function(url) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                // Mostrar notificación de copiado
                this.showNotification('URL copiada al portapapeles');
            }).catch(err => {
                console.log('Error copiando al portapapeles:', err);
            });
        }
    },
    
    /**
     * Muestra una notificación temporal
     * @param {string} message - Mensaje a mostrar
     */
    showNotification: function(message) {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
};

// Inicialización automática cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initPublicInfoPage);

// Exportar funciones para uso externo si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initPublicInfoPage,
        publicInfoUtils: window.publicInfoUtils
    };
}