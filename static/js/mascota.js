/**
 * Script para la gestión de mascotas y datos biométricos
 * Maneja las pestañas y el slider horizontal
 */

document.addEventListener("DOMContentLoaded", function () {
    // Inicializar pestañas
    initTabs();

    // Inicializar slider de datos biométricos
    initBiometricSlider();
    
    // Inicializar funcionalidades adicionales
    initAdditionalFeatures();
});

/**
 * Inicializa las pestañas en la interfaz de mascotas
 */
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (!tabButtons.length || !tabContents.length) {
        console.log('No se encontraron pestañas para inicializar');
        return;
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Obtener el target desde el data-target
            const target = button.getAttribute('data-target');
            
            if (!target) {
                console.warn('Botón de pestaña sin data-target:', button);
                return;
            }
            
            // Actualizar botones activos
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                // Resetear estilos de botón inactivo usando la paleta personalizada
                btn.classList.add('text-neutral-500');
                btn.classList.remove('text-primary-600', 'border-primary-500');
                btn.classList.add('border-transparent');
            });
            
            // Activar botón actual con colores de la paleta personalizada
            button.classList.add('active');
            button.classList.remove('text-neutral-500', 'border-transparent');
            button.classList.add('text-primary-600', 'border-primary-500');
            
            // Mostrar el contenido correspondiente
            tabContents.forEach(content => {
                content.classList.add('hidden');
                if (content.getAttribute('id') === target) {
                    content.classList.remove('hidden');
                    
                    // Si es la pestaña de datos biométricos, reinicializar el slider
                    if (target === 'datos-biometricos') {
                        // Pequeño delay para asegurar que el contenido esté visible
                        setTimeout(() => {
                            initBiometricSlider();
                        }, 100);
                    }
                    
                    // Si es la pestaña de mi mascota, realizar animaciones adicionales
                    if (target === 'mi-mascota') {
                        setTimeout(() => {
                            // Agregar animaciones de entrada para las tarjetas
                            const cards = content.querySelectorAll('.space-y-4, .bg-white, .bg-gray-50');
                            cards.forEach((card, index) => {
                                setTimeout(() => {
                                    card.style.opacity = '0';
                                    card.style.transform = 'translateY(20px)';
                                    card.style.transition = 'all 0.4s ease-out';
                                    
                                    setTimeout(() => {
                                        card.style.opacity = '1';
                                        card.style.transform = 'translateY(0)';
                                    }, 50);
                                }, index * 100);
                            });
                        }, 100);
                    }
                }
            });
            
            // Agregar efecto de transición suave
            const activeContent = document.getElementById(target);
            if (activeContent) {
                activeContent.style.opacity = '0';
                activeContent.classList.remove('hidden');
                
                // Fade in effect
                setTimeout(() => {
                    activeContent.style.transition = 'opacity 0.3s ease-in-out';
                    activeContent.style.opacity = '1';
                }, 10);
            }
        });
    });
    
    console.log('Pestañas inicializadas correctamente');
}

/**
 * Inicializa el slider horizontal para datos biométricos
 */
function initBiometricSlider() {
    const prevButtons = document.querySelectorAll('.biometric-prev');
    const nextButtons = document.querySelectorAll('.biometric-next');
    const slides = document.querySelectorAll('.biometric-slide');
    const indicators = document.querySelectorAll('.slide-indicator');
    const totalSlides = slides.length;

    if (!totalSlides) {
        console.log('No se encontraron slides biométricos');
        return;
    }

    let currentSlide = 0;

    // Actualiza la visualización del slider
    function updateSlider() {
        slides.forEach((slide, index) => {
            if (index === currentSlide) {
                slide.classList.remove('hidden');
                slide.style.opacity = '1';
            } else {
                slide.classList.add('hidden');
                slide.style.opacity = '0';
            }
        });

        // Actualizar indicadores
        indicators.forEach((indicator, index) => {
            if (index === currentSlide) {
                indicator.classList.add('active');
                indicator.classList.add('w-6', 'bg-primary-500');
                indicator.classList.remove('w-2', 'bg-gray-300');
            } else {
                indicator.classList.remove('active');
                indicator.classList.remove('w-6', 'bg-primary-500');
                indicator.classList.add('w-2', 'bg-gray-300');
            }
        });

        // Actualizar estado de botones prev/next
        prevButtons.forEach(btn => {
            btn.disabled = currentSlide === 0;
            btn.classList.toggle('opacity-50', currentSlide === 0);
            btn.classList.toggle('cursor-not-allowed', currentSlide === 0);
        });

        nextButtons.forEach(btn => {
            if (currentSlide === totalSlides - 1) {
                btn.innerHTML = 'Finalizar <i class="fas fa-check ml-2"></i>';
                btn.classList.add('bg-green-600', 'hover:bg-green-700');
                btn.classList.remove('bg-primary-600', 'hover:bg-primary-700');
            } else {
                btn.innerHTML = 'Siguiente <i class="fas fa-arrow-right ml-2"></i>';
                btn.classList.remove('bg-green-600', 'hover:bg-green-700');
                btn.classList.add('bg-primary-600', 'hover:bg-primary-700');
            }
            
            btn.disabled = false;
            btn.classList.remove('opacity-50');
        });
    }

    // Configurar botones prev
    prevButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentSlide > 0) {
                currentSlide--;
                updateSlider();
            }
        });
    });

    // Configurar botones next
    nextButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentSlide < totalSlides - 1) {
                currentSlide++;
                updateSlider();
            } else {
                // Estamos en la última diapositiva
                handleBiometricFinish();
            }
        });
    });

    // Configurar indicadores
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', (e) => {
            e.preventDefault();
            currentSlide = index;
            updateSlider();
        });
    });

    // Inicializar el slider
    updateSlider();
    
    console.log(`Slider biométrico inicializado con ${totalSlides} slides`);
}

/**
 * Maneja la finalización del registro biométrico
 */
function handleBiometricFinish() {
    console.log("Finalizado el slider biométrico");
    
    // Aquí puedes agregar lógica para enviar los datos
    // Por ejemplo, mostrar un modal de confirmación
    if (confirm('¿Está seguro de que desea finalizar el registro biométrico?')) {
        // Simular envío de datos
        console.log('Enviando datos biométricos...');
        
        // Opcional: regresar a la primera pestaña después de finalizar
        setTimeout(() => {
            const registroNormalTab = document.querySelector('[data-target="registro-normal"]');
            if (registroNormalTab) {
                registroNormalTab.click();
            }
        }, 1000);
    }
}

/**
 * Inicializa funcionalidades adicionales
 */
function initAdditionalFeatures() {
    // Manejo de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            // Prevenir envío por defecto para demostración
            e.preventDefault();
            console.log('Formulario enviado (modo demostración)');
        });
    });
    
    // Manejo de upload de archivos
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const uploadBtn = input.nextElementSibling;
        if (uploadBtn && uploadBtn.tagName === 'BUTTON') {
            uploadBtn.addEventListener('click', () => {
                input.click();
            });
            
            input.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    const fileName = e.target.files[0].name;
                    uploadBtn.innerHTML = `<i class="fas fa-check text-green-500 mr-2"></i>${fileName}`;
                    uploadBtn.classList.add('bg-green-100', 'text-green-700');
                }
            });
        }
    });
    
    console.log('Funcionalidades adicionales inicializadas');
}