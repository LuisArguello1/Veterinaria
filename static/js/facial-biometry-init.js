/**
 * Script de inicialización para el sistema de biometría facial
 * Maneja la configuración e inicialización del FacialRecognitionManager
 */

(function() {
    'use strict';
    
    console.log('Facial Biometry Init Script loaded');
    
    // Inicializar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, checking configuration...');
        
        // Verificar que la configuración esté disponible
        if (typeof window.FACIAL_CONFIG === 'undefined') {
            console.error('FACIAL_CONFIG no está definido');
            return;
        }
        
        console.log('Configuration:', window.FACIAL_CONFIG);
        
        // Verificar que el manager esté disponible
        if (typeof FacialRecognitionManager === 'undefined') {
            console.error('FacialRecognitionManager no está cargado');
            return;
        }
        
        console.log('FacialRecognitionManager loaded:', typeof FacialRecognitionManager);
        
        try {
            // Inicializar el sistema de reconocimiento facial
            const manager = initFacialRecognition(window.FACIAL_CONFIG);
            console.log('Facial recognition initialized successfully:', manager);
            
            // Hacer disponible globalmente para debugging
            window.facialManager = manager;
            
        } catch (error) {
            console.error('Error initializing facial recognition:', error);
            
            // Mostrar error al usuario
            const errorMessage = document.createElement('div');
            errorMessage.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #fee2e2;
                border-left: 4px solid #ef4444;
                color: #991b1b;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                z-index: 9999;
                max-width: 400px;
                font-size: 14px;
                animation: slideIn 0.3s ease;
            `;
            
            errorMessage.innerHTML = `
                <div style="display: flex; align-items: start; gap: 0.75rem;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 1.25rem; margin-top: 2px;"></i>
                    <div>
                        <strong style="display: block; margin-bottom: 0.25rem;">Error al inicializar</strong>
                        <span>${error.message || 'Error desconocido'}</span>
                    </div>
                </div>
            `;
            
            document.body.appendChild(errorMessage);
            
            // Remover mensaje después de 8 segundos
            setTimeout(() => {
                errorMessage.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => errorMessage.remove(), 300);
            }, 8000);
        }
    });
    
    // Agregar animaciones CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
})();
