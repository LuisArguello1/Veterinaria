/**
 * Script para la gestión de mascotas y datos biométricos
 * Maneja las pestañas y el slider horizontal, así como la captura y subida de imágenes biométricas
 * 
 * VERSIÓN ACTUALIZADA - NO INTERCEPTA FORMULARIOS DE REGISTRO
 */

// Variable global para el estado de la cámara biométrica
let biometricCameraActive = false;

// Función para verificar y corregir el estado de la cámara biométrica
function verificarEstadoCameraBiometrica() {
    const webcamVideo = document.getElementById('webcam');
    const startCameraBtn = document.getElementById('start-camera');
    
    const tieneVideo = webcamVideo && webcamVideo.srcObject;
    
    if (biometricCameraActive && !tieneVideo) {
        // Estado inconsistente: dice que está activa pero no hay video
        console.log('Corrigiendo estado inconsistente biométrico: activa->inactiva');
        biometricCameraActive = false;
        if (startCameraBtn) {
            startCameraBtn.innerHTML = '<i class="fas fa-play mr-2"></i> Iniciar cámara';
            startCameraBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
            startCameraBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
        }
    } else if (!biometricCameraActive && tieneVideo) {
        // Estado inconsistente: dice que está inactiva pero hay video
        console.log('Corrigiendo estado inconsistente biométrico: inactiva->activa');
        biometricCameraActive = true;
        if (startCameraBtn) {
            startCameraBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> Detener cámara';
            startCameraBtn.classList.remove('bg-primary-600', 'hover:bg-primary-700');
            startCameraBtn.classList.add('bg-red-600', 'hover:bg-red-700');
        }
    }
    
    return biometricCameraActive;
}

// Función global para detener la cámara biométrica (accesible desde otras partes)
window.stopBiometricCamera = function() {
    console.log('=== INICIANDO stopBiometricCamera ===');
    console.log('Estado inicial biometricCameraActive:', biometricCameraActive);
    
    const webcamVideo = document.getElementById('webcam');
    const startCameraBtn = document.getElementById('start-camera');
    const capturePhotoBtn = document.getElementById('capture-photo');
    const cameraOverlay = document.getElementById('camera-overlay');
    const cameraSelectContainer = document.getElementById('camera-select-container');
    
    console.log('Elementos encontrados:', {
        webcamVideo: !!webcamVideo,
        startCameraBtn: !!startCameraBtn,
        capturePhotoBtn: !!capturePhotoBtn,
        cameraOverlay: !!cameraOverlay,
        cameraSelectContainer: !!cameraSelectContainer,
        hasVideoSrc: !!(webcamVideo && webcamVideo.srcObject)
    });
    
    if (webcamVideo && webcamVideo.srcObject) {
        console.log('Deteniendo tracks del video...');
        const tracks = webcamVideo.srcObject.getTracks();
        console.log('Tracks encontrados:', tracks.length);
        tracks.forEach(track => {
            console.log('Deteniendo track:', track.kind, track.readyState);
            track.stop();
        });
        webcamVideo.srcObject = null;
        console.log('Video srcObject limpiado');
    } else {
        console.log('No hay video o srcObject para detener');
    }
    
    // Marcar cámara como inactiva globalmente
    biometricCameraActive = false;
    console.log('Estado actualizado biometricCameraActive:', biometricCameraActive);
    
    // Disparar evento de cambio de estado
    window.dispatchEvent(new CustomEvent('biometricCameraStateChanged', {
        detail: { 
            active: false,
            timestamp: new Date().getTime()
        }
    }));
    
    // Restaurar botón de iniciar cámara
    if (startCameraBtn) {
        console.log('Actualizando botón de cámara...');
        startCameraBtn.innerHTML = '<i class="fas fa-play mr-2"></i> Iniciar cámara';
        startCameraBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
        startCameraBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
        console.log('Botón actualizado');
    } else {
        console.log('startCameraBtn no encontrado');
    }
    
    // Deshabilitar botón de captura
    if (capturePhotoBtn) {
        capturePhotoBtn.disabled = true;
        console.log('Botón de captura deshabilitado');
    }
    
    // Ocultar selector de cámaras
    if (cameraSelectContainer) {
        cameraSelectContainer.style.display = 'none';
        console.log('Selector de cámaras ocultado');
    }
    
    // Mostrar overlay inicial
    if (cameraOverlay) {
        cameraOverlay.innerHTML = '<i class="fas fa-video mr-2"></i> Presiona "Iniciar cámara" para comenzar';
        cameraOverlay.classList.remove('hidden');
        console.log('Overlay restaurado');
    }
    
    console.log('=== stopBiometricCamera COMPLETADO ===');
};

document.addEventListener("DOMContentLoaded", function () {
    console.log('Inicializando funcionalidades de mascota.js...');

    // Comprobar si estamos en una página de mascota válida
    const mascotaId = new URLSearchParams(window.location.search).get('id');
    if (!mascotaId) {
        console.log('No se detectó un ID de mascota en la URL. Algunas funcionalidades pueden estar limitadas.');
        
        // NO inicializamos el selector aquí, se hará cuando se cambie a la pestaña
    }
    
    // Inicializar pestañas
    initTabs();

    // Inicializar slider de datos biométricos
    initBiometricSlider();
    
    // Inicializar captura de cámara y subida de fotos (si estamos en la página correcta)
    const cameraElements = document.getElementById('webcam') || document.getElementById('start-camera');
    if (cameraElements) {
        console.log('Inicializando captura de cámara...');
        initCameraCapture();
    }
    
    // Inicializar subida de archivos
    const fileElements = document.getElementById('file-input') || document.getElementById('select-files-btn');
    if (fileElements) {
        console.log('Inicializando subida de archivos...');
        initFileUpload();
    }
    
    // Inicializar galería de imágenes
    const galleryElement = document.getElementById('gallery-container');
    if (galleryElement) {
        console.log('Inicializando galería...');
        initGallery();
    }
    
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
    
    console.log('Inicializando sistema de pestañas...');
    
    // Verificar si hay que activar automáticamente la pestaña de biometría
    const activeBiometriaId = window.appConfig?.activeBiometriaId;
    let defaultTab = 'mi-mascota';
    
    if (activeBiometriaId) {
        defaultTab = 'datos-biometricos';
        console.log(`Activando automáticamente pestaña de biometría para mascota ID: ${activeBiometriaId}`);
    }
    
    // Inicializar estado - mantener mi-mascota visible y ocultar otros
    // El div mi-mascota siempre mantiene display:block, pero controlamos el contenido
    tabContents.forEach(content => {
        if (content.id === 'mi-mascota') {
            content.style.display = 'block';
            // Mostrar contenido de mi-mascota por defecto, excepto si se especifica otra pestaña
            const miMascotaContent = document.getElementById('mi-mascota-content');
            if (miMascotaContent) {
                if (defaultTab === 'mi-mascota') {
                    miMascotaContent.classList.remove('hidden');
                } else {
                    miMascotaContent.classList.add('hidden');
                }
            }
        } else {
            // Otras pestañas ocultas por defecto, excepto si es la pestaña por defecto
            if (content.id === defaultTab) {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        }
    });

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
                btn.classList.add('text-gray-500');
                btn.classList.remove('text-primary-600', 'border-primary-500');
                btn.classList.add('border-transparent');
            });
            
            // Activar botón actual con colores de la paleta personalizada
            button.classList.add('active');
            button.classList.remove('text-gray-500', 'border-transparent');
            button.classList.add('text-primary-600', 'border-primary-500');
            
            console.log(`Cambiando a pestaña: ${target}`);
            
            // Controlar visibilidad de contenidos
            if (target === 'mi-mascota') {
                // Mostrar mi-mascota (que siempre tiene display:block) y su contenido
                document.getElementById('mi-mascota').style.display = 'block';
                document.getElementById('registro-normal').style.display = 'none';
                document.getElementById('datos-biometricos').style.display = 'none';
                
                // Mostrar contenido de mi-mascota
                const miMascotaContent = document.getElementById('mi-mascota-content');
                if (miMascotaContent) {
                    miMascotaContent.classList.remove('hidden');
                }
                
            } else if (target === 'registro-normal') {
                // Ocultar contenido de mi-mascota pero mantener el div principal visible
                const miMascotaContent = document.getElementById('mi-mascota-content');
                if (miMascotaContent) {
                    miMascotaContent.classList.add('hidden');
                }
                
                // Mostrar registro normal
                document.getElementById('mi-mascota').style.display = 'block'; // Mantenemos siempre visible
                document.getElementById('registro-normal').style.display = 'block';
                document.getElementById('datos-biometricos').style.display = 'none';
                
            } else if (target === 'datos-biometricos') {
                // Ocultar contenido de mi-mascota pero mantener el div principal visible
                const miMascotaContent = document.getElementById('mi-mascota-content');
                if (miMascotaContent) {
                    miMascotaContent.classList.add('hidden');
                }
                
                // Mostrar datos biométricos
                document.getElementById('mi-mascota').style.display = 'block'; // Mantenemos siempre visible
                document.getElementById('registro-normal').style.display = 'none';
                document.getElementById('datos-biometricos').style.display = 'block';
                
                // Inicializar funcionalidades específicas de biometría
                setTimeout(() => {
                    const mascotaId = new URLSearchParams(window.location.search).get('id');
                    
                    if (mascotaId) {
                        // Si hay un ID, inicializar el slider biométrico
                        initBiometricSlider();
                    } else {
                        // Si no hay ID, mostrar el selector de mascotas
                        if (!document.getElementById('mascota-selector-container')) {
                            try {
                                console.log("Inicializando selector de mascotas...");
                                initMascotaSelector();
                            } catch (error) {
                                console.warn("Error al inicializar el selector de mascotas:", error);
                            }
                        }
                    }
                }, 100);
            }
        });
    });
    
    // Activar el botón correcto al inicio
    tabButtons.forEach(button => {
        const target = button.getAttribute('data-target');
        if (target === defaultTab) {
            button.classList.add('active', 'text-primary-600', 'border-primary-500');
            button.classList.remove('text-gray-500', 'border-transparent');
        } else {
            button.classList.remove('active', 'text-primary-600', 'border-primary-500');
            button.classList.add('text-gray-500', 'border-transparent');
        }
    });
    
    // Si hay un activeBiometriaId, cargar automáticamente el contenido biométrico
    if (activeBiometriaId && defaultTab === 'datos-biometricos') {
        setTimeout(() => {
            loadBiometricContentForMascota(activeBiometriaId);
        }, 500);
    }
    
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
        console.log('No se encontraron slides biométricos - esto es normal si aún no se ha seleccionado una mascota');
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
/**
 * Inicializa la captura de imágenes con la cámara web
 */
function initCameraCapture() {
    console.log('Inicializando captura de cámara...', {
        currentMascotaId: window.currentMascotaId,
        urlId: new URLSearchParams(window.location.search).get('id')
    });
    
    // Verificar si ya está inicializada para evitar múltiples listeners
    const startCameraBtn = document.getElementById('start-camera');
    if (startCameraBtn && startCameraBtn._biometricInitialized) {
        console.log('Captura de cámara ya inicializada, saltando...');
        return;
    }
    
    // Elementos del DOM
    const capturePhotoBtn = document.getElementById('capture-photo');
    const savePhotoBtn = document.getElementById('save-photo');
    const discardPhotoBtn = document.getElementById('discard-photo');
    const webcamVideo = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const capturedImage = document.getElementById('captured-image');
    const placeholder = document.getElementById('placeholder');
    const cameraOverlay = document.getElementById('camera-overlay');
    const uploadForm = document.getElementById('upload-form');
    const imagenBase64Input = document.getElementById('imagen_base64');
    const cameraSelect = document.getElementById('camera-select');
    const cameraSelectContainer = document.getElementById('camera-select-container');
    const switchCameraBtn = document.getElementById('switch-camera');
    
    // Variables
    let stream = null;
    let photoTaken = false;
    let currentDeviceId = '';
    let buttonClickInProgress = false; // Para evitar clicks múltiples
    
    // Si no existen los elementos esenciales, salir
    if (!startCameraBtn || !webcamVideo) {
        console.log('No se encontraron elementos de cámara necesarios');
        return;
    }
    
    // Función para obtener dispositivos de cámara disponibles
    async function getCameraDevices() {
        try {
            // Primero pedir acceso a la cámara para obtener etiquetas
            const initialStream = await navigator.mediaDevices.getUserMedia({ video: true });
            // Cerrar el stream inicial después de obtener permisos
            initialStream.getTracks().forEach(track => track.stop());
            
            // Ahora enumerar todos los dispositivos
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            
            // Limpiar selector
            if (cameraSelect) {
                cameraSelect.innerHTML = '';
                
                // Si no hay dispositivos
                if (videoDevices.length === 0) {
                    const option = document.createElement('option');
                    option.text = 'No se encontraron cámaras';
                    option.value = '';
                    cameraSelect.add(option);
                    if (switchCameraBtn) switchCameraBtn.disabled = true;
                    return [];
                }
                
                // Agregar opciones al selector
                videoDevices.forEach((device, index) => {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.text = device.label || `Cámara ${index + 1}`;
                    cameraSelect.add(option);
                });
                
                // Habilitar botón de cambio si hay más de una cámara
                if (switchCameraBtn) switchCameraBtn.disabled = videoDevices.length <= 1;
                
                // Mostrar el contenedor del selector
                if (cameraSelectContainer) cameraSelectContainer.style.display = 'block';
            }
            
            return videoDevices;
        } catch (err) {
            console.error('Error al enumerar dispositivos:', err);
            return [];
        }
    }
    
    // Inicializar selector de cámaras al cargar la página
    getCameraDevices().catch(err => console.error('Error al inicializar cámaras:', err));
    
    // Manejar cambio de cámara desde el selector
    if (cameraSelect) {
        cameraSelect.addEventListener('change', async () => {
            currentDeviceId = cameraSelect.value;
            
            // Si la cámara ya está iniciada, reiniciarla con la nueva selección
            if (stream && biometricCameraActive) {
                console.log('Cambiando de cámara, reiniciando...');
                // Detener usando la función global pero sin cambiar el estado (es solo un cambio de dispositivo)
                const webcamVideo = document.getElementById('webcam');
                if (webcamVideo && webcamVideo.srcObject) {
                    const tracks = webcamVideo.srcObject.getTracks();
                    tracks.forEach(track => track.stop());
                    webcamVideo.srcObject = null;
                }
                stream = null;
                // Reiniciar con el nuevo dispositivo
                await startCamera(currentDeviceId);
            }
        });
    }
    
    // Botón para cambiar cámara rápidamente
    if (switchCameraBtn) {
        switchCameraBtn.addEventListener('click', async () => {
            // Si no hay un select válido, no hacer nada
            if (!cameraSelect || cameraSelect.options.length <= 1) return;
            
            // Encontrar el siguiente índice
            let nextIndex = 0;
            for (let i = 0; i < cameraSelect.options.length; i++) {
                if (cameraSelect.options[i].value === currentDeviceId) {
                    nextIndex = (i + 1) % cameraSelect.options.length;
                    break;
                }
            }
            
            // Seleccionar siguiente cámara
            cameraSelect.selectedIndex = nextIndex;
            currentDeviceId = cameraSelect.value;
            
            // Si la cámara ya está iniciada, reiniciarla con la nueva selección
            if (stream && biometricCameraActive) {
                console.log('Cambiando de cámara rápidamente, reiniciando...');
                // Detener usando la función global pero sin cambiar el estado (es solo un cambio de dispositivo)
                const webcamVideo = document.getElementById('webcam');
                if (webcamVideo && webcamVideo.srcObject) {
                    const tracks = webcamVideo.srcObject.getTracks();
                    tracks.forEach(track => track.stop());
                    webcamVideo.srcObject = null;
                }
                stream = null;
                // Reiniciar con el nuevo dispositivo
                await startCamera(currentDeviceId);
            }
        });
    }
    
    // Función para iniciar la cámara
    async function startCamera(deviceId = null) {
        console.log('=== startCamera llamada ===', {
            deviceId,
            currentState: biometricCameraActive,
            hasStream: !!stream,
            stackTrace: new Error().stack
        });
        
        try {
            // Mostrar overlay de inicialización
            if (cameraOverlay) {
                cameraOverlay.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Inicializando cámara...';
                cameraOverlay.classList.remove('hidden');
            }
            
            // Si ya hay un stream activo, detenerlo primero
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                stream = null;
            }
            
            // Configurar restricciones
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
                audio: false
            };
            
            // Si se proporciona un ID de dispositivo, usarlo
            if (deviceId) {
                constraints.video.deviceId = { exact: deviceId };
                currentDeviceId = deviceId;
            } else if (currentDeviceId) {
                constraints.video.deviceId = { exact: currentDeviceId };
            } else {
                // De lo contrario, preferir cámara trasera en móviles
                constraints.video.facingMode = { ideal: 'environment' };
            }
            
            console.log('Iniciando cámara con restricciones:', constraints);
            
            // Solicitar acceso a la cámara
            stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Actualizar lista de dispositivos si no se ha hecho antes
            if (!deviceId && !currentDeviceId) {
                const devices = await getCameraDevices();
                
                if (devices && devices.length > 0) {
                    // Obtener el dispositivo actual del stream
                    const track = stream.getVideoTracks()[0];
                    const settings = track.getSettings();
                    
                    // Actualizar el selector si hay un deviceId
                    if (settings.deviceId && cameraSelect) {
                        currentDeviceId = settings.deviceId;
                        cameraSelect.value = currentDeviceId;
                    }
                }
            }
            
            // Asignar stream al elemento video
            if (webcamVideo) {
                webcamVideo.srcObject = stream;
                await webcamVideo.play();
            }
            
            // Habilitar botón de captura
            if (capturePhotoBtn) capturePhotoBtn.disabled = false;
            
            // Cambiar estado del botón de iniciar cámara
            if (startCameraBtn) {
                startCameraBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> Detener cámara';
                startCameraBtn.classList.remove('bg-primary-600', 'hover:bg-primary-700');
                startCameraBtn.classList.add('bg-red-600', 'hover:bg-red-700');
            }
            
            // Marcar cámara como activa
            biometricCameraActive = true;
            console.log('Cámara biométrica iniciada, estado:', biometricCameraActive);
            
            // Establecer variable global para otros scripts
            window.biometricCameraActive = true;
            
            // Disparar evento de cambio de estado
            window.dispatchEvent(new CustomEvent('biometricCameraStateChanged', {
                detail: { 
                    active: true,
                    timestamp: new Date().getTime()
                }
            }));
            
            // Reiniciar completamente el módulo de captura automática después de activar la cámara
            console.log('Reinicializando módulo de captura automática después de activar la cámara');
            setTimeout(() => {
                // Llamar a la función de inicialización con reintento
                if (typeof initWithRetry === 'function') {
                    initWithRetry();
                } else if (typeof window.initWithRetry === 'function') {
                    window.initWithRetry();
                } else {
                    console.log('Función initWithRetry no encontrada, intentando inicializar directamente');
                    if (window.BiometriaCapturaAutomatica && typeof window.BiometriaCapturaAutomatica.init === 'function') {
                        window.BiometriaCapturaAutomatica.init();
                    }
                }
                
                // Asegurarnos de que el botón esté habilitado
                setTimeout(() => {
                    const startAutoBtn = document.getElementById('start-auto-capture');
                    if (startAutoBtn) {
                        console.log('Habilitando botón de captura automática después de reinicializar');
                        startAutoBtn.disabled = false;
                    } else {
                        console.log('No se encontró el botón de captura automática después de reinicializar');
                    }
                }, 300);
            }, 500); // Pequeño retraso para asegurar que todo esté listo
            
            // Ocultar overlay cuando la cámara esté lista
            if (cameraOverlay) cameraOverlay.classList.add('hidden');
            return true;
        } catch (err) {
            console.error('Error al acceder a la cámara:', err);
            alert('No se pudo acceder a la cámara. Por favor, verifica que has concedido permisos.');
            if (cameraOverlay) {
                cameraOverlay.innerHTML = '<i class="fas fa-video-slash mr-2"></i> Error al inicializar cámara. Presiona "Iniciar cámara" para reintentar.';
            }
            biometricCameraActive = false; // Asegurar que el estado sea correcto
            window.biometricCameraActive = false; // Actualizar variable global también
            return false;
        }
    }
    
    // Iniciar cámara cuando se haga clic en el botón
    if (startCameraBtn) {
        console.log('Agregando event listener al botón de cámara biométrica');
        startCameraBtn.addEventListener('click', async (event) => {
            // Prevenir propagación para evitar múltiples ejecuciones
            event.preventDefault();
            event.stopPropagation();
            
            // Evitar clicks múltiples
            if (buttonClickInProgress) {
                console.log('Click ignorado - operación en progreso');
                return;
            }
            
            buttonClickInProgress = true;
            
            try {
                console.log('Estado actual de cámara biométrica:', biometricCameraActive);
                
                if (biometricCameraActive) {
                    // Si la cámara está activa, detenerla
                    console.log('Deteniendo cámara biométrica...');
                    window.stopBiometricCamera();
                } else {
                    // Si la cámara no está activa, iniciarla
                    console.log('Iniciando cámara biométrica...');
                    await startCamera(currentDeviceId);
                }
            } finally {
                // Liberar el lock después de un pequeño delay
                setTimeout(() => {
                    buttonClickInProgress = false;
                }, 500);
            }
        });
        
        // Marcar como inicializado para evitar múltiples listeners
        startCameraBtn._biometricInitialized = true;
        console.log('Botón de cámara biométrica marcado como inicializado');
    }
    
    // Función para detener la cámara (simplificada - usa la función global)
    function stopCamera() {
        console.log('stopCamera local llamada');
        // Usar la función global
        window.stopBiometricCamera();
        // Limpiar variable local
        stream = null;
    }
    
    // Función para capturar foto
    if (capturePhotoBtn) {
        capturePhotoBtn.addEventListener('click', () => {
            if (!stream || !webcamVideo || !canvas) return;
            
            console.log('Capturando foto biométrica, estado antes:', biometricCameraActive);
            
            try {
                // Configurar canvas con dimensiones del video
                canvas.width = webcamVideo.videoWidth;
                canvas.height = webcamVideo.videoHeight;
                
                // Dibujar frame actual del video en el canvas
                const context = canvas.getContext('2d');
                context.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
                
                // Convertir a imagen
                const imageDataUrl = canvas.toDataURL('image/jpeg');
                
                if (capturedImage) {
                    capturedImage.src = imageDataUrl;
                    
                    // Mostrar solo la imagen capturada, mantener canvas oculto
                    capturedImage.classList.remove('hidden');
                    // El canvas debe mantenerse oculto para evitar imagen doble
                    if (placeholder) placeholder.classList.add('hidden');
                }
                
                // Habilitar botones de guardar/descartar
                if (savePhotoBtn) savePhotoBtn.disabled = false;
                if (discardPhotoBtn) discardPhotoBtn.disabled = false;
                
                // Guardar estado
                photoTaken = true;
                
                // Almacenar imagen en formulario
                if (imagenBase64Input) imagenBase64Input.value = imageDataUrl;
            } catch (err) {
                console.error('Error al capturar foto:', err);
                showToast('Error al capturar foto', 'error');
            }
        });
    }
    
    // Función para guardar foto
    if (savePhotoBtn) {
        savePhotoBtn.addEventListener('click', async () => {
            if (!photoTaken) return;
            
            try {
                // Mostrar mensaje de carga
                savePhotoBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Guardando...';
                savePhotoBtn.disabled = true;
                
                // Obtener el ID de la mascota desde múltiples fuentes
                let mascotaId = null;
                
                // 1. Intentar desde la URL
                mascotaId = new URLSearchParams(window.location.search).get('id');
                
                // 2. Si no está en la URL, intentar desde la variable global
                if (!mascotaId && window.currentMascotaId) {
                    mascotaId = window.currentMascotaId;
                }
                
                // 3. Si no está disponible globalmente, intentar desde los campos hidden
                if (!mascotaId) {
                    const hiddenMascotaId = document.querySelector('input[name="mascota_id"]');
                    if (hiddenMascotaId && hiddenMascotaId.value) {
                        mascotaId = hiddenMascotaId.value;
                    }
                }
                
                // 4. Intentar desde el data-attribute del contenedor biométrico
                if (!mascotaId) {
                    const biometriaContent = document.querySelector('.biometria-content');
                    if (biometriaContent && biometriaContent.getAttribute('data-mascota-id')) {
                        mascotaId = biometriaContent.getAttribute('data-mascota-id');
                    }
                }
                
                if (!mascotaId) {
                    showToast('Error: No se ha seleccionado una mascota. Primero debe crear o seleccionar una mascota.', 'error');
                    console.error('No se pudo obtener el ID de la mascota desde ninguna fuente');
                    return;
                }
                
                console.log(`Usando mascota ID: ${mascotaId}`);
                
                // Enviar formulario mediante fetch
                const formData = new FormData(uploadForm);
                // Asegurarse de que se envía el ID de la mascota
                if (!formData.has('mascota_id')) {
                    formData.append('mascota_id', mascotaId);
                }
                
                const response = await fetch('/mascota/upload-biometria-base64/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.success) {
                        // Mostrar mensaje de éxito
                        showToast('Imagen guardada correctamente', 'success');
                        
                        // Actualizar barra de progreso
                        updateProgressBar(data.images_count, 20);
                        
                        // Actualizar galería
                        updateGallery();
                        
                        // Verificar si se alcanzó el límite
                        if (data.limit_reached) {
                            disableCaptureInterface('Has alcanzado el límite de 20 imágenes biométricas para esta mascota.');
                        }
                        
                        // Restaurar interfaz
                        resetCaptureInterface();
                    } else {
                        showToast(data.error || 'Error al guardar la imagen', 'error');
                        
                        // Si es límite alcanzado, deshabilitar interfaz
                        if (data.limit_reached) {
                            disableCaptureInterface(data.error);
                        }
                    }
                } else {
                    // Tratar de obtener el mensaje de error
                    try {
                        const errorData = await response.json();
                        showToast(errorData.error || `Error ${response.status}: No se pudo guardar la imagen`, 'error');
                    } catch (jsonError) {
                        showToast(`Error ${response.status}: No se pudo guardar la imagen`, 'error');
                    }
                }
            } catch (err) {
                console.error('Error al guardar la imagen:', err);
                showToast('Error al guardar la imagen', 'error');
            } finally {
                savePhotoBtn.innerHTML = '<i class="fas fa-save mr-2"></i> Guardar foto';
                savePhotoBtn.disabled = false;
            }
        });
    }
    
    // Función para descartar foto
    if (discardPhotoBtn) {
        discardPhotoBtn.addEventListener('click', () => {
            resetCaptureInterface();
        });
    }
    
    // Función para restaurar interfaz de captura
    function resetCaptureInterface() {
        // Verificar que los elementos existen
        if (capturedImage) capturedImage.classList.add('hidden');
        if (canvas) canvas.classList.add('hidden');
        if (placeholder) placeholder.classList.remove('hidden');
        
        // Deshabilitar botones de guardar/descartar
        if (savePhotoBtn) savePhotoBtn.disabled = true;
        if (discardPhotoBtn) discardPhotoBtn.disabled = true;
        
        // Resetear estado
        photoTaken = false;
    }
}

/**
 * Inicializa la subida de archivos
 */
function initFileUpload() {
    console.log('Inicializando subida de archivos...', {
        currentMascotaId: window.currentMascotaId,
        urlId: new URLSearchParams(window.location.search).get('id')
    });
    const fileInput = document.getElementById('file-input');
    const selectFilesBtn = document.getElementById('select-files-btn');
    const uploadFilesBtn = document.getElementById('upload-files-btn');
    const filePreviewContainer = document.getElementById('file-preview-container');
    const fileUploadForm = document.getElementById('file-upload-form');
    
    // Si no existen los elementos, salir
    if (!fileInput || !selectFilesBtn) return;
    
    // Evento para abrir el selector de archivos
    selectFilesBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Área de arrastrar y soltar
    const dropZone = selectFilesBtn.parentElement;
    
    // Eventos de arrastrar y soltar
    ['dragover', 'dragenter'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('bg-primary-50', 'border-primary-400');
        }, false);
    });
    
    ['dragleave', 'dragend', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('bg-primary-50', 'border-primary-400');
            
            if (eventName === 'drop') {
                const files = e.dataTransfer.files;
                fileInput.files = files;
                handleFileSelect(files);
            }
        }, false);
    });
    
    // Manejar selección de archivos
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files);
    });
    
    // Función para manejar archivos seleccionados
    function handleFileSelect(files) {
        if (!files || files.length === 0) return;
        
        // Validar que no se suban más de 20 imágenes
        if (files.length > 20) {
            showToast('Solo puedes subir un máximo de 20 imágenes por vez', 'error');
            fileInput.value = ''; // Limpiar la selección
            return;
        }
        
        // Limpiar previsualizaciones anteriores
        const previewGrid = filePreviewContainer.querySelector('div');
        if (previewGrid) {
            previewGrid.innerHTML = '';
        }
        filePreviewContainer.classList.remove('hidden');
        
        // Mostrar previsualizaciones
        Array.from(files).forEach((file, index) => {
            if (!file.type.startsWith('image/')) return;
            
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const preview = document.createElement('div');
                preview.className = 'relative group';
                preview.innerHTML = `
                    <div class="h-24 sm:h-32 w-full rounded-md overflow-hidden bg-gray-100 border border-gray-200">
                        <img src="${e.target.result}" alt="Vista previa" class="h-full w-full object-cover">
                    </div>
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100">
                        <button type="button" class="remove-file-btn bg-red-600 hover:bg-red-700 text-white p-1 rounded-full" data-index="${index}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="text-xs text-gray-500 mt-1 truncate">${file.name}</div>
                `;
                
                const previewGrid = filePreviewContainer.querySelector('div');
                if (previewGrid) {
                    previewGrid.appendChild(preview);
                } else {
                    filePreviewContainer.appendChild(preview);
                }
                
                // Evento para eliminar archivo
                const removeBtn = preview.querySelector('.remove-file-btn');
                removeBtn.addEventListener('click', () => {
                    preview.remove();
                    
                    // Si no hay más previsualizaciones, ocultar contenedor
                    if (filePreviewContainer.children.length === 0) {
                        filePreviewContainer.classList.add('hidden');
                        uploadFilesBtn.disabled = true;
                    }
                });
            };
            
            reader.readAsDataURL(file);
        });
        
        // Habilitar botón de subida si hay archivos
        uploadFilesBtn.disabled = files.length === 0;
    }
    
    // Evento de envío del formulario
    fileUploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files || fileInput.files.length === 0) return;
        
        try {
            // Obtener el ID de la mascota desde múltiples fuentes
            let mascotaId = null;
            
            // 1. Intentar desde el formulario
            const formData = new FormData(fileUploadForm);
            mascotaId = formData.get('mascota_id');
            
            // 2. Si no está en el formulario, intentar desde la variable global
            if (!mascotaId && window.currentMascotaId) {
                mascotaId = window.currentMascotaId;
                formData.set('mascota_id', mascotaId);
            }
            
            // 3. Si no está disponible globalmente, intentar desde la URL
            if (!mascotaId) {
                mascotaId = new URLSearchParams(window.location.search).get('id');
                if (mascotaId) {
                    formData.set('mascota_id', mascotaId);
                }
            }
            
            // 4. Intentar desde el data-attribute del contenedor biométrico
            if (!mascotaId) {
                const biometriaContent = document.querySelector('.biometria-content');
                if (biometriaContent && biometriaContent.getAttribute('data-mascota-id')) {
                    mascotaId = biometriaContent.getAttribute('data-mascota-id');
                    formData.set('mascota_id', mascotaId);
                }
            }
            
            if (!mascotaId) {
                showToast('Error: No se ha seleccionado una mascota. Primero debe crear o seleccionar una mascota.', 'error');
                console.error('No se pudo obtener el ID de la mascota para subir archivos');
                return;
            }
            
            console.log(`Subiendo archivos para mascota ID: ${mascotaId}`);
            
            // Mostrar mensaje de carga con número de archivos
            const fileCount = fileInput.files.length;
            uploadFilesBtn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> Subiendo ${fileCount} imagen${fileCount > 1 ? 'es' : ''}...`;
            uploadFilesBtn.disabled = true;
            
            const response = await fetch(fileUploadForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // Mostrar mensaje de éxito más detallado
                    let successMessage = `${data.count} imagen${data.count > 1 ? 'es' : ''} subida${data.count > 1 ? 's' : ''} correctamente`;
                    if (data.images_count !== undefined) {
                        successMessage += ` (${data.images_count}/20)`;
                    }
                    showToast(successMessage, 'success');
                    
                    // Actualizar barra de progreso inmediatamente si hay datos
                    if (data.images_count !== undefined) {
                        updateProgressBar(data.images_count, 20);
                    }
                    
                    // Actualizar galería
                    updateGallery();
                    
                    // Restaurar interfaz
                    filePreviewContainer.innerHTML = '';
                    filePreviewContainer.classList.add('hidden');
                    fileInput.value = '';
                    
                    // Recargar la página después de un breve delay para mostrar el toast y la actualización
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    // Manejar errores específicos
                    let errorMessage = data.error || 'Error al subir imágenes';
                    if (data.images_remaining !== undefined) {
                        errorMessage += ` Solo puedes subir ${data.images_remaining} imagen${data.images_remaining > 1 ? 'es' : ''} más.`;
                    }
                    showToast(errorMessage, 'error');
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                showToast(errorData.error || 'Error del servidor al subir imágenes', 'error');
            }
        } catch (err) {
            console.error('Error al subir imágenes:', err);
            showToast('Error al subir imágenes', 'error');
        } finally {
            uploadFilesBtn.innerHTML = '<i class="fas fa-upload mr-2"></i> Subir imágenes';
            uploadFilesBtn.disabled = false;
        }
    });
}

/**
 * Inicializa la galería de imágenes
 */
function initGallery() {
    const galleryContainer = document.getElementById('gallery-container');
    const trainModelBtn = document.getElementById('train-model-btn');
    
    // Si no existe el contenedor, salir
    if (!galleryContainer) return;
    
    // Manejar eliminación de imágenes
    galleryContainer.addEventListener('click', async (e) => {
        const deleteBtn = e.target.closest('.delete-image-btn');
        if (!deleteBtn) return;
        
        const imageId = deleteBtn.dataset.id;
        if (!imageId) return;
        
        if (confirm('¿Estás seguro de que deseas eliminar esta imagen?')) {
            try {
                const response = await fetch(`/mascota/delete-imagen/${imageId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.success) {
                        // Eliminar elemento del DOM
                        deleteBtn.closest('.image-card').remove();
                        
                        // Actualizar contador
                        updateGallery();
                        
                        showToast('Imagen eliminada correctamente', 'success');
                    } else {
                        showToast(data.error || 'Error al eliminar la imagen', 'error');
                    }
                } else {
                    showToast('Error al eliminar la imagen', 'error');
                }
            } catch (err) {
                console.error('Error al eliminar la imagen:', err);
                showToast('Error al eliminar la imagen', 'error');
            }
        }
    });
    
    // Manejar entrenamiento del modelo
    if (trainModelBtn) {
        trainModelBtn.addEventListener('click', async () => {
            if (confirm('¿Deseas iniciar el entrenamiento del modelo biométrico? Este proceso puede tardar unos minutos.')) {
                try {
                    // Mostrar mensaje de carga
                    trainModelBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Entrenando...';
                    trainModelBtn.disabled = true;
                    
                    const mascotaId = new URLSearchParams(window.location.search).get('id');
                    
                    const response = await fetch(`/mascota/train-model/${mascotaId || 0}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        if (data.success) {
                            showToast('Modelo entrenado correctamente', 'success');
                            
                            // Recargar página para actualizar estado
                            setTimeout(() => {
                                location.reload();
                            }, 2000);
                        } else {
                            showToast(data.error || 'Error al entrenar el modelo', 'error');
                        }
                    } else {
                        showToast('Error al entrenar el modelo', 'error');
                    }
                } catch (err) {
                    console.error('Error al entrenar el modelo:', err);
                    showToast('Error al entrenar el modelo', 'error');
                } finally {
                    trainModelBtn.innerHTML = '<i class="fas fa-brain mr-2"></i> Entrenar modelo biométrico';
                    trainModelBtn.disabled = false;
                }
            }
        });
    }
}

/**
 * Actualiza la galería de imágenes y estadísticas
 */
async function updateGallery() {
    // Obtener el ID de la mascota desde múltiples fuentes
    let mascotaId = null;
    
    // 1. Intentar desde la variable global
    if (window.currentMascotaId) {
        mascotaId = window.currentMascotaId;
    }
    
    // 2. Si no está disponible globalmente, intentar desde la URL
    if (!mascotaId) {
        mascotaId = new URLSearchParams(window.location.search).get('id');
    }
    
    // 3. Intentar desde el data-attribute del contenedor biométrico
    if (!mascotaId) {
        const biometriaContent = document.querySelector('.biometria-content');
        if (biometriaContent && biometriaContent.getAttribute('data-mascota-id')) {
            mascotaId = biometriaContent.getAttribute('data-mascota-id');
        }
    }
    
    // 4. Intentar desde los campos hidden
    if (!mascotaId) {
        const hiddenMascotaId = document.querySelector('input[name="mascota_id"]');
        if (hiddenMascotaId && hiddenMascotaId.value) {
            mascotaId = hiddenMascotaId.value;
        }
    }
    
    if (!mascotaId) {
        console.warn('No se pudo actualizar la galería: No hay ID de mascota disponible');
        return;
    }
    
    try {
        console.log(`Actualizando galería para mascota ID: ${mascotaId}`);
        const response = await fetch(`/mascota/get-stats/${mascotaId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Estadísticas recibidas:', data);
            
            // Actualizar contadores
            const imageCount = document.querySelector('[data-stats="image-count"]');
            if (imageCount) {
                imageCount.textContent = `${data.images_count} / 20`;
            }
            
            // Actualizar progreso
            const progressBar = document.querySelector('[data-stats="progress-bar"]');
            if (progressBar) {
                const percent = Math.min(data.images_count / 20 * 100, 100);
                progressBar.style.width = `${percent}%`;
            }
            
            // Recargar galería si es necesario
            if (data.reload_gallery) {
                location.reload();
            }
        } else {
            console.error(`Error al obtener estadísticas: ${response.status}`);
            
            // Si es un error 404, posiblemente la mascota no existe
            if (response.status === 404) {
                showToast('Esta mascota no existe o no tiene acceso a ella', 'error');
            }
        }
    } catch (err) {
        console.error('Error al actualizar estadísticas:', err);
    }
}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'info') {
    // Si existe la función global de notificación, usarla
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
        return;
    }
    
    // Si no, crear notificación simple
    const toast = document.createElement('div');
    toast.className = `fixed bottom-5 right-5 p-4 rounded-md shadow-lg z-50 ${
        type === 'success' ? 'bg-green-600' : 
        type === 'error' ? 'bg-red-600' : 
        type === 'warning' ? 'bg-yellow-600' : 
        'bg-blue-600'
    } text-white`;
    
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${
                type === 'success' ? 'check-circle' : 
                type === 'error' ? 'exclamation-circle' : 
                type === 'warning' ? 'exclamation-triangle' : 
                'info-circle'
            } mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('opacity-0', 'transition-opacity', 'duration-500');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 500);
    }, 3000);
}

/**
 * Obtiene el valor de una cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // ¿Esta cookie tiene el nombre que buscamos?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Inicializa el selector de mascotas para asociar datos biométricos
 */
function initMascotaSelector() {
    console.log('Inicializando selector de mascotas...');
    
    // Verificar si el selector ya existe para evitar duplicados
    if (document.getElementById('mascota-selector-container')) {
        console.log('El selector de mascotas ya existe, no se inicializa de nuevo.');
        return;
    }
    
    // Crear el contenedor del selector
    const selectorContainer = document.createElement('div');
    selectorContainer.className = 'mb-6 bg-white p-4 rounded-lg shadow-sm border border-primary-100 relative z-10';
    selectorContainer.id = 'mascota-selector-container';
    selectorContainer.style.display = 'block'; // Asegurarse de que sea visible
    
    selectorContainer.innerHTML = `
        <div class="flex items-center mb-4">
            <div class="flex-shrink-0 mr-3">
                <i class="fas fa-paw text-primary-600 text-xl"></i>
            </div>
            <div>
                <h3 class="font-semibold text-gray-800">Selecciona una mascota</h3>
                <p class="text-sm text-gray-500">Antes de continuar, debes seleccionar a qué mascota pertenecen los datos biométricos</p>
            </div>
        </div>
        
        <div class="flex flex-col md:flex-row items-center gap-3">
            <div class="w-full">
                <select id="mascota-select" class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
                    <option value="">Cargando mascotas...</option>
                </select>
            </div>
            <div class="flex gap-2">
                <button id="select-mascota-btn" class="bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-md flex items-center justify-center" disabled>
                    <i class="fas fa-check mr-2"></i> Seleccionar
                </button>
            </div>
        </div>
        
        <div id="mascota-warning" class="mt-4 hidden">
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <i class="fas fa-exclamation-triangle text-yellow-400"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-yellow-700">
                            No tienes mascotas registradas. Debes crear al menos una mascota antes de registrar datos biométricos.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
        // Buscar dónde insertar el selector (en el contenedor específico)
    const biometriaContent = document.querySelector('.biometria-content');
    const biometriaSelectorContainer = document.getElementById('biometria-selector-container');
    const biometriaContentContainer = document.getElementById('biometria-content-container');
    
    if (biometriaSelectorContainer) {
        // Estamos en la página principal con tabs y tenemos el contenedor específico
        console.log("Encontrado el contenedor para el selector de mascotas");
        
        // Insertar el selector en el contenedor específico
        biometriaSelectorContainer.innerHTML = '';
        biometriaSelectorContainer.appendChild(selectorContainer);
        
        // Ocultar el contenido de biometría hasta que se seleccione una mascota
        if (biometriaContentContainer) {
            biometriaContentContainer.style.display = 'none';
        }
    } else if (biometriaContent) {
        // Estamos en la página específica de biometría
        console.log("Insertando selector en la página específica de biometría");
        biometriaContent.parentNode.insertBefore(selectorContainer, biometriaContent);
        // Ocultar el contenido biométrico hasta que se seleccione una mascota
        biometriaContent.style.display = 'none';
    } else {
        console.log("No se encontró ni el contenedor del selector ni el contenido de biometría");
    }
    
    // Cargar las mascotas del usuario
    loadUserPets();
    
    // Función para cargar las mascotas del usuario
    async function loadUserPets() {
        try {
            // Mostrar un estado de carga
            const selectElement = document.getElementById('mascota-select');
            if (selectElement) {
                selectElement.innerHTML = '<option value="">Cargando mascotas...</option>';
            }
            
            const response = await fetch('/mascota/get-user-pets/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                const selectElement = document.getElementById('mascota-select');
                const selectButton = document.getElementById('select-mascota-btn');
                const warningElement = document.getElementById('mascota-warning');
                
                // Limpiar selector
                selectElement.innerHTML = '';
                
                if (data.mascotas && data.mascotas.length > 0) {
                    // Agregar opción por defecto
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = 'Selecciona una mascota...';
                    selectElement.appendChild(defaultOption);
                    
                    // Agregar las mascotas
                    data.mascotas.forEach(mascota => {
                        const option = document.createElement('option');
                        option.value = mascota.id;
                        option.textContent = `${mascota.nombre} (${mascota.especie} - ${mascota.raza})`;
                        selectElement.appendChild(option);
                    });
                    
                    // Habilitar botón de selección cuando se elige una mascota
                    selectElement.addEventListener('change', () => {
                        selectButton.disabled = !selectElement.value;
                    });
                    
                    // Configurar botón de selección
                    selectButton.addEventListener('click', () => {
                        const selectedId = selectElement.value;
                        if (selectedId) {
                            // En lugar de redirigir, cargar el contenido biométrico en la pestaña actual
                            loadBiometricContentForMascota(selectedId);
                        }
                    });
                } else {
                    // Mostrar mensaje si no hay mascotas
                    selectElement.innerHTML = '<option value="">No hay mascotas registradas</option>';
                    selectElement.disabled = true;
                    selectButton.disabled = true;
                    
                    if (warningElement) {
                        warningElement.classList.remove('hidden');
                    }
                }
                
                // Configurar botón de creación de mascota
                const createButton = document.getElementById('create-mascota-btn');
                if (createButton) {
                    createButton.addEventListener('click', () => {
                        window.location.href = '/mascota/crear/';
                    });
                }
            } else {
                const errorText = await response.text();
                console.error('Error al cargar las mascotas:', errorText);
                
                // Mostrar un mensaje de error amigable
                const selectElement = document.getElementById('mascota-select');
                if (selectElement) {
                    selectElement.innerHTML = '<option value="">Error al cargar mascotas</option>';
                    selectElement.disabled = true;
                }
                
                showToast('Error al cargar tus mascotas', 'error');
            }
        } catch (err) {
            console.error('Error al cargar las mascotas:', err);
            
            // Mostrar un mensaje de error amigable
            const selectElement = document.getElementById('mascota-select');
            if (selectElement) {
                selectElement.innerHTML = '<option value="">Error al cargar mascotas</option>';
                selectElement.disabled = true;
            }
            
            showToast('Error al cargar tus mascotas', 'error');
        }
    }
}

/**
 * Carga el contenido biométrico para una mascota específica
 */
async function loadBiometricContentForMascota(mascotaId) {
    console.log(`Cargando contenido biométrico para mascota ID: ${mascotaId}`);
    
    try {
        // Mostrar loading
        const biometriaContentContainer = document.getElementById('biometria-content-container');
        const selectorContainer = document.getElementById('biometria-selector-container');
        
        if (biometriaContentContainer) {
            biometriaContentContainer.innerHTML = `
                <div class="flex items-center justify-center py-8">
                    <div class="text-center">
                        <i class="fas fa-spinner fa-spin text-3xl text-primary-500 mb-3"></i>
                        <p class="text-gray-600">Cargando datos biométricos...</p>
                    </div>
                </div>
            `;
            biometriaContentContainer.style.display = 'block';
            biometriaContentContainer.style.visibility = 'visible';
        }
        
        // Hacer petición para obtener el contenido biométrico
        const response = await fetch(`/mascota/${mascotaId}/biometria/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            const html = await response.text();
            
            // Extraer solo el contenido biométrico del HTML completo
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const biometricContent = doc.querySelector('.biometria-content');
            
            if (biometricContent && biometriaContentContainer) {
                // Ocultar el selector y mostrar el contenido biométrico  
                if (selectorContainer) {
                    selectorContainer.style.display = 'none';
                }
                
                // Insertar el contenido biométrico
                biometriaContentContainer.innerHTML = biometricContent.outerHTML;
                biometriaContentContainer.style.display = 'block';
                biometriaContentContainer.style.visibility = 'visible';
                
                // Almacenar el ID de la mascota globalmente
                window.currentMascotaId = mascotaId;
                
                // Actualizar todos los campos hidden con el ID correcto
                const hiddenMascotaIds = biometriaContentContainer.querySelectorAll('input[name="mascota_id"]');
                hiddenMascotaIds.forEach(input => {
                    input.value = mascotaId;
                });
                
                // También actualizar el data-attribute del contenedor principal
                const biometriaContent = biometriaContentContainer.querySelector('.biometria-content');
                if (biometriaContent) {
                    biometriaContent.setAttribute('data-mascota-id', mascotaId);
                }
                
                // Reinicializar las funcionalidades biométricas
                setTimeout(() => {
                    initBiometricSlider();
                    initCameraCapture();
                    initFileUpload();
                    initGallery();
                    
                    // Verificar límites iniciales para esta mascota
                    checkInitialLimits();
                    
                    // Asegurar que las funciones tienen acceso al ID
                    console.log(`Funcionalidades biométricas inicializadas para mascota: ${mascotaId}`);
                }, 100);
                
                // Agregar botón para volver al selector
                const backButton = document.createElement('div');
                backButton.className = 'mb-4';
                backButton.innerHTML = `
                    <button id="back-to-selector" class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                        <i class="fas fa-arrow-left mr-2"></i>
                        Cambiar mascota
                    </button>
                `;
                biometriaContentContainer.insertBefore(backButton, biometriaContentContainer.firstChild);
                
                // Configurar el botón de volver
                document.getElementById('back-to-selector').addEventListener('click', () => {
                    if (selectorContainer) {
                        selectorContainer.style.display = 'block';
                    }
                    if (biometriaContentContainer) {
                        biometriaContentContainer.style.display = 'none';
                        biometriaContentContainer.innerHTML = '';
                    }
                    
                    // Limpiar selección
                    const selectElement = document.getElementById('mascota-select');
                    if (selectElement) {
                        selectElement.value = '';
                    }
                    const selectButton = document.getElementById('select-mascota-btn');
                    if (selectButton) {
                        selectButton.disabled = true;
                    }
                });
                
                showToast('Contenido biométrico cargado correctamente', 'success');
            } else {
                throw new Error('No se pudo extraer el contenido biométrico');
            }
        } else {
            throw new Error(`Error HTTP: ${response.status}`);
        }
    } catch (error) {
        console.error('Error al cargar el contenido biométrico:', error);
        
        if (biometriaContentContainer) {
            biometriaContentContainer.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                        <div>
                            <h3 class="text-red-800 font-medium">Error al cargar</h3>
                            <p class="text-red-700 text-sm mt-1">No se pudo cargar el contenido biométrico. Por favor, intente nuevamente.</p>
                        </div>
                    </div>
                    <button id="retry-load" class="mt-3 inline-flex items-center px-3 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100">
                        <i class="fas fa-redo mr-2"></i>
                        Intentar nuevamente
                    </button>
                </div>
            `;
            
            // Configurar botón de reintentar
            document.getElementById('retry-load').addEventListener('click', () => {
                loadBiometricContentForMascota(mascotaId);
            });
        }
        
        showToast('Error al cargar el contenido biométrico', 'error');
    }
}

/**
 * Inicializa funcionalidades adicionales
 */
function initAdditionalFeatures() {
    // FUNCIÓN TEMPORALMENTE DESHABILITADA PARA EVITAR CONFLICTOS CON EL FORMULARIO
    // La funcionalidad de upload de archivos se mantiene en otras funciones específicas
    
    console.log('initAdditionalFeatures: Función deshabilitada - formularios funcionan normalmente');
    
    // Si necesitas funcionalidades específicas de upload, se pueden agregar aquí
    // pero SIN interceptar el evento submit de formularios
}

/**
 * Actualiza la barra de progreso de imágenes biométricas
 * @param {number} current - Número actual de imágenes
 * @param {number} max - Número máximo de imágenes (20)
 */
function updateProgressBar(current, max) {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');
    
    if (progressBar && progressText) {
        const percentage = (current / max) * 100;
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `${current}/${max}`;
        
        // Cambiar color según el progreso
        if (percentage >= 100) {
            progressBar.className = 'progress-bar bg-green-500 h-full rounded transition-all duration-300';
        } else if (percentage >= 75) {
            progressBar.className = 'progress-bar bg-yellow-500 h-full rounded transition-all duration-300';
        } else {
            progressBar.className = 'progress-bar bg-blue-500 h-full rounded transition-all duration-300';
        }
    }
}

/**
 * Deshabilita la interfaz de captura cuando se alcanza el límite
 * @param {string} message - Mensaje a mostrar
 */
function disableCaptureInterface(message) {
    const captureButtons = document.querySelectorAll('#start-camera, #capture-photo, #select-files-btn');
    const uploadArea = document.querySelector('.upload-area');
    
    captureButtons.forEach(btn => {
        if (btn) {
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    });
    
    if (uploadArea) {
        uploadArea.classList.add('opacity-50', 'pointer-events-none');
    }
    
    // Mostrar mensaje de límite alcanzado
    showLimitReachedMessage(message);
}

/**
 * Muestra un mensaje cuando se alcanza el límite de imágenes
 * @param {string} message - Mensaje a mostrar
 */
function showLimitReachedMessage(message = 'Has alcanzado el límite de 20 imágenes biométricas para esta mascota.') {
    console.log('Mostrando mensaje de límite alcanzado:', message);
    
    const container = document.querySelector('#biometric-content') || document.querySelector('.biometria-content') || document.getElementById('biometria-content-container');
    if (!container) {
        console.warn('No se encontró contenedor para mostrar el mensaje de límite');
        return;
    }
    
    // Verificar si ya existe el mensaje
    let limitMessage = container.querySelector('.limit-reached-message');
    if (!limitMessage) {
        limitMessage = document.createElement('div');
        limitMessage.className = 'limit-reached-message bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-md mb-4';
        container.insertBefore(limitMessage, container.firstChild);
    }
    
    limitMessage.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <i class="fas fa-check-circle text-green-500"></i>
            </div>
            <div class="ml-3">
                <h3 class="text-green-800 font-medium">¡Límite alcanzado!</h3>
                <p class="text-green-700 text-sm mt-1">${message}</p>
            </div>
        </div>
    `;
}

/**
 * Función para verificar límites iniciales al cargar la página
 */
function checkInitialLimits() {
    console.log('Verificando límites iniciales');
    
    // Obtener el ID de la mascota desde múltiples fuentes
    let mascotaId = null;
    
    if (window.currentMascotaId) {
        mascotaId = window.currentMascotaId;
    } else {
        mascotaId = new URLSearchParams(window.location.search).get('id');
    }
    
    const mascotaSelect = document.getElementById('mascota-select');
    if (mascotaSelect && mascotaSelect.value) {
        mascotaId = mascotaSelect.value;
    }
    
    if (!mascotaId) {
        console.log('No hay ID de mascota para verificar límites');
        return;
    }
    
    // Hacer una consulta al servidor para obtener el estado actual
    fetch(`/mascota/get-stats/${mascotaId}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data && data.images_count !== undefined) {
            console.log(`Estado inicial: ${data.images_count}/20 imágenes`);
            
            // Actualizar barra de progreso
            updateProgressBar(data.images_count, 20);
            
            // Si se alcanzó el límite, deshabilitar interfaz
            if (data.images_count >= 20) {
                disableCaptureInterface('Has alcanzado el límite de 20 imágenes biométricas para esta mascota.');
            }
        }
    })
    .catch(error => {
        console.error('Error al verificar límites iniciales:', error);
    });
}

/**
 * Función para inicializar los límites cuando se cambia de mascota
 */
function initializeLimitsForMascota() {
    console.log('Inicializando límites para la mascota seleccionada');
    
    // Esperar un poco para que el contenido se haya actualizado
    setTimeout(() => {
        checkInitialLimits();
    }, 500);
}