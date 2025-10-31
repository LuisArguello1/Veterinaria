/**
 * biometria_captura.js - Módulo especializado para la captura automática de imágenes biométricas
 * 
 * Este módulo extiende la funcionalidad del sistema de biometría para permitir:
 * - Captura automática de múltiples imágenes
 * - Captura en intervalo configurable
 * - Visualización en miniaturas de las capturas
 * - Guardado masivo de imágenes
 */

// Namespace para la captura automática biométrica
window.BiometriaCapturaAutomatica = (function() {
    // Estado interno
    let isRunning = false;
    let currentCount = 0;
    let targetCount = 0;
    let interval = 0;
    let captureTimer = null;
    let capturedImages = [];
    let mascotaId = null;
    
    // Cache de elementos DOM
    let elements = {
        startAutoBtn: null,
        progressBar: null,
        progressContainer: null,
        countDisplay: null,
        thumbnailsContainer: null,
        thumbnailsGrid: null,
        saveAllBtn: null,
        countInput: null,
        intervalInput: null
    };
    
    /**
     * Inicializa el módulo de captura automática
     */
    function init() {
        console.log('Inicializando módulo de captura automática biométrica');
        
        // Cargar elementos del DOM
        elements.startAutoBtn = document.getElementById('start-auto-capture');
        elements.progressContainer = document.getElementById('auto-capture-progress');
        elements.progressBar = document.getElementById('auto-capture-progress-bar');
        elements.countDisplay = document.getElementById('auto-capture-count-display');
        elements.thumbnailsContainer = document.getElementById('auto-capture-thumbnails');
        elements.thumbnailsGrid = elements.thumbnailsContainer?.querySelector('.grid');
        elements.saveAllBtn = document.getElementById('save-all-photos');
        elements.countInput = document.getElementById('auto-capture-count');
        elements.intervalInput = document.getElementById('auto-capture-interval');
        
        // Verificar si los elementos se encontraron correctamente
        console.log('Elemento startAutoBtn encontrado:', !!elements.startAutoBtn);
        
        // Verificar la variable global de cámara activa
        console.log('Estado de la cámara al inicializar módulo:', window.biometricCameraActive);
        
        if (elements.startAutoBtn) {
            console.log('Estado inicial del botón, disabled:', elements.startAutoBtn.disabled);
            
            // Si la cámara ya está activa, asegurar que el botón esté habilitado
            if (window.biometricCameraActive === true) {
                console.log('Cámara ya activa, habilitando botón inmediatamente');
                elements.startAutoBtn.disabled = false;
            }
        }
        
        // Verificar si estamos en la sección con mascota seleccionada
        const biometriaContent = document.querySelector('.biometria-content');
        const hasMascotaSelected = biometriaContent && biometriaContent.getAttribute('data-mascota-id');
        
        // Si no hay mascota seleccionada, no es un error, simplemente no inicializamos
        if (!hasMascotaSelected) {
            console.log('No hay mascota seleccionada, el módulo de captura automática se activará cuando se seleccione una mascota');
            return;
        }
        
        // Si no existen los elementos esenciales, ahora sí reportar error
        if (!elements.startAutoBtn || !elements.progressContainer) {
            console.error('No se encontraron elementos necesarios para captura automática, pero hay una mascota seleccionada');
            return;
        }
        
        // Configurar event listeners
        if (elements.startAutoBtn) {
            console.log('Añadiendo event listener al botón de captura automática');
            elements.startAutoBtn.addEventListener('click', toggleAutoCapture);
            
            // Verificar si el botón está deshabilitado por defecto y habilitar si la cámara ya está activa
            if (elements.startAutoBtn.disabled && window.biometricCameraActive === true) {
                console.log('Cámara ya activa, habilitando botón');
                elements.startAutoBtn.disabled = false;
            }
        } else {
            console.error('No se encontró el botón de captura automática');
        }
        
        if (elements.saveAllBtn) {
            elements.saveAllBtn.addEventListener('click', saveAllCapturedImages);
        }
        
        // Actualizar el límite máximo del campo de número de fotos según la cantidad disponible
        function updateMaxCaptures() {
            if (elements.countInput) {
                const currentImages = getCurrentImageCount();
                const remainingImages = 20 - currentImages;
                
                if (remainingImages > 0) {
                    console.log(`Actualizando límite de capturas: ${remainingImages} disponibles`);
                    elements.countInput.max = remainingImages;
                    elements.countInput.title = `Puedes capturar hasta ${remainingImages} fotos más`;
                    
                    // Si el valor actual es mayor que el permitido, ajustarlo
                    if (parseInt(elements.countInput.value) > remainingImages) {
                        elements.countInput.value = remainingImages;
                    }
                    
                    // Actualizar o añadir mensaje informativo
                    const countContainer = elements.countInput.closest('div');
                    if (countContainer) {
                        let infoNote = countContainer.querySelector('.remaining-info');
                        if (!infoNote) {
                            infoNote = document.createElement('div');
                            infoNote.className = 'remaining-info text-xs text-blue-600 mt-1';
                            countContainer.appendChild(infoNote);
                        }
                        infoNote.textContent = `Máximo permitido: ${remainingImages} fotos`;
                    }
                } else {
                    // Si ya no quedan imágenes disponibles
                    elements.countInput.max = 0;
                    elements.countInput.value = 0;
                    elements.countInput.disabled = true;
                    elements.countInput.title = 'Has alcanzado el límite de 20 imágenes';
                    
                    // Deshabilitar el botón de captura automática
                    disableCaptureInterface('Has alcanzado el límite de 20 imágenes biométricas');
                }
            }
        }
        
        // Llamar inicialmente para configurar el límite
        updateMaxCaptures();
        
        // Habilitar botón cuando se inicia la cámara
        window.addEventListener('biometricCameraStateChanged', function(event) {
            console.log('Evento biometricCameraStateChanged recibido:', event.detail);
            if (event.detail && event.detail.active) {
                console.log('Habilitando botón de captura automática');
                if (elements.startAutoBtn) {
                    elements.startAutoBtn.disabled = false;
                    console.log('Botón de captura automática habilitado:', elements.startAutoBtn);
                }
                // Actualizar el límite máximo de capturas
                updateMaxCaptures();
            } else {
                console.log('Deshabilitando botón de captura automática');
                if (elements.startAutoBtn) elements.startAutoBtn.disabled = true;
                // Si la cámara se detiene mientras estamos en captura automática, detener también
                if (isRunning) {
                    stopAutoCapture();
                }
            }
        });
        
        console.log('Módulo de captura automática inicializado');
    }
    
    /**
     * Obtiene el número actual de imágenes biométricas guardadas
     * @returns {number} - Número de imágenes actuales
     */
    function getCurrentImageCount() {
        const biometriaContent = document.querySelector('.biometria-content');
        if (biometriaContent) {
            const imagesCountText = biometriaContent.querySelector('.text-gray-800.font-bold');
            if (imagesCountText) {
                const countMatch = imagesCountText.textContent.match(/(\d+)\s*\/\s*20/);
                if (countMatch) {
                    return parseInt(countMatch[1]);
                }
            }
        }
        return 0;
    }
    
    /**
     * Deshabilita la interfaz de captura cuando se alcanza el límite de imágenes
     * @param {string} message - Mensaje a mostrar
     */
    function disableCaptureInterface(message) {
        // Deshabilitar botón de captura
        if (elements.startAutoBtn) {
            elements.startAutoBtn.disabled = true;
            elements.startAutoBtn.title = message;
        }
        
        // Mostrar mensaje al usuario
        showToast(message, 'warning');
        
        // Añadir notificación en la interfaz
        const captureSection = document.querySelector('.camera-capture-section');
        if (captureSection) {
            const limitAlert = document.createElement('div');
            limitAlert.className = 'bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-3 mt-3';
            limitAlert.innerHTML = `
                <i class="fas fa-exclamation-triangle mr-2"></i> ${message}
            `;
            captureSection.prepend(limitAlert);
        }
    }
    
    /**
     * Inicia o detiene la captura automática según el estado actual
     */
    function toggleAutoCapture(event) {
        console.log('Función toggleAutoCapture llamada');
        
        // Prevenir comportamiento por defecto si es un evento
        if (event) {
            event.preventDefault();
            event.stopPropagation();
            console.log('Evento recibido:', event);
        }
        
        // Verificar si se ha alcanzado el límite de imágenes
        const currentImageCount = getCurrentImageCount();
        const remaining = 20 - currentImageCount;
        
        if (remaining <= 0) {
            disableCaptureInterface('Has alcanzado el límite de 20 imágenes biométricas para esta mascota.');
            return;
        }
        
        // Verificar nuevamente que tenemos los elementos necesarios
        if (!elements.startAutoBtn || !elements.progressContainer) {
            console.error('Elementos para captura automática no disponibles');
            console.error('Intentando obtenerlos de nuevo...');
            
            elements.startAutoBtn = document.getElementById('start-auto-capture');
            elements.progressContainer = document.getElementById('auto-capture-progress');
            elements.progressBar = document.getElementById('auto-capture-progress-bar');
            elements.countDisplay = document.getElementById('auto-capture-count-display');
            
            if (!elements.startAutoBtn || !elements.progressContainer) {
                alert('Error: No se pudieron encontrar los elementos necesarios para la captura automática. Por favor, recarga la página.');
                return;
            }
        }
        
        console.log('Estado botón:', elements.startAutoBtn.disabled);
        console.log('Estado cámara global:', window.biometricCameraActive);
        
        if (isRunning) {
            stopAutoCapture();
        } else {
            startAutoCapture();
        }
    }
    
    /**
     * Inicia el proceso de captura automática
     */
    function startAutoCapture() {
        console.log('Iniciando proceso de captura automática...');
        
        // Verificar que la cámara esté activa
        if (!window.biometricCameraActive) {
            console.error('La cámara no está activa, estado:', window.biometricCameraActive);
            
            // Verificar manualmente si el video está funcionando aunque la bandera indique lo contrario
            const webcamVideo = document.getElementById('webcam');
            if (webcamVideo && webcamVideo.srcObject && webcamVideo.srcObject.active) {
                console.warn('La bandera biometricCameraActive es false pero el video parece estar activo. Corrigiendo...');
                window.biometricCameraActive = true;
            } else {
                showToast('La cámara debe estar activa para usar captura automática', 'error');
                return;
            }
        }
        
        // Obtener configuración del usuario
        targetCount = parseInt(elements.countInput?.value || 5);
        interval = parseInt(elements.intervalInput?.value || 2) * 1000; // convertir a milisegundos
        
        // Validar parámetros y verificar límites disponibles
        const currentImages = getCurrentImageCount();
        const remainingImages = 20 - currentImages;
        
        if (targetCount < 1) {
            showToast('El número de fotos debe ser al menos 1', 'error');
            return;
        }
        
        if (targetCount > remainingImages) {
            showToast(`Solo puedes capturar ${remainingImages} fotos más. Ajustando automáticamente...`, 'warning');
            targetCount = remainingImages;
            if (elements.countInput) elements.countInput.value = remainingImages;
        }
        
        if (interval < 1000 || interval > 10000) {
            showToast('El intervalo debe estar entre 1 y 10 segundos', 'error');
            return;
        }
        
        // Si no quedan imágenes disponibles, no permitir la captura
        if (remainingImages <= 0) {
            showToast('Has alcanzado el límite de 20 imágenes biométricas', 'error');
            return;
        }
        
        // Inicializar captura
        console.log(`Iniciando captura automática: ${targetCount} fotos, intervalo ${interval}ms`);
        isRunning = true;
        currentCount = 0;
        capturedImages = [];
        
        // Actualizar UI
        elements.startAutoBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> Detener captura';
        elements.startAutoBtn.classList.remove('bg-gradient-to-r', 'from-blue-600', 'to-indigo-600', 'hover:from-blue-700', 'hover:to-indigo-700');
        elements.startAutoBtn.classList.add('bg-red-600', 'hover:bg-red-700');
        
        // Mostrar barra de progreso
        if (elements.progressContainer) elements.progressContainer.classList.remove('hidden');
        updateProgressBar(0);
        
        // Mostrar contenedor de miniaturas y limpiar
        if (elements.thumbnailsContainer && elements.thumbnailsGrid) {
            elements.thumbnailsContainer.classList.remove('hidden');
            elements.thumbnailsGrid.innerHTML = '';
        }
        
        // Iniciar el proceso de captura automática
        nextAutoCapture();
    }
    
    /**
     * Realiza la siguiente captura automática en secuencia
     */
    function nextAutoCapture() {
        if (!isRunning || currentCount >= targetCount) {
            finishAutoCapture();
            return;
        }
        
        // Programar la siguiente captura
        captureTimer = setTimeout(() => {
            // Realizar captura
            captureImage()
                .then(imageData => {
                    // Incrementar contador
                    currentCount++;
                    
                    // Guardar imagen capturada
                    capturedImages.push(imageData);
                    
                    // Actualizar progreso
                    updateProgressBar(currentCount / targetCount * 100);
                    
                    // Crear y mostrar miniatura
                    addThumbnail(imageData);
                    
                    // Continuar con la siguiente captura
                    nextAutoCapture();
                })
                .catch(error => {
                    console.error('Error en captura automática:', error);
                    showToast('Error al capturar imagen', 'error');
                    stopAutoCapture();
                });
        }, interval);
    }
    
    /**
     * Detiene el proceso de captura automática
     */
    function stopAutoCapture() {
        console.log('Deteniendo captura automática');
        
        // Limpiar temporizador
        if (captureTimer) {
            clearTimeout(captureTimer);
            captureTimer = null;
        }
        
        // Actualizar estado
        isRunning = false;
        
        // Actualizar UI
        resetAutoCaptureUI();
    }
    
    /**
     * Finaliza el proceso de captura automática con éxito
     */
    function finishAutoCapture() {
        // Detener proceso
        isRunning = false;
        
        // Limpiar temporizador
        if (captureTimer) {
            clearTimeout(captureTimer);
            captureTimer = null;
        }
        
        // Actualizar UI
        resetAutoCaptureUI();
        
        // Mostrar mensaje de éxito
        showToast(`Captura automática completada: ${capturedImages.length} imágenes capturadas`, 'success');
    }
    
    /**
     * Captura una imagen desde la cámara web
     * @returns {Promise<string>} - Promise con la imagen en formato base64
     */
    function captureImage() {
        return new Promise((resolve, reject) => {
            try {
                const webcamVideo = document.getElementById('webcam');
                const canvas = document.getElementById('canvas');
                
                if (!webcamVideo || !canvas) {
                    reject(new Error('Elementos de cámara no encontrados'));
                    return;
                }
                
                // Verificar que el video esté recibiendo datos
                if (!webcamVideo.srcObject || webcamVideo.videoWidth === 0) {
                    console.error('Video no inicializado correctamente:', {
                        hasSrcObject: !!webcamVideo.srcObject,
                        videoWidth: webcamVideo.videoWidth,
                        videoHeight: webcamVideo.videoHeight,
                        readyState: webcamVideo.readyState
                    });
                    reject(new Error('La cámara no está inicializada correctamente'));
                    return;
                }
                
                // Intentar usar la API ImageCapture si está disponible
                if (window.ImageCapture && webcamVideo.srcObject) {
                    try {
                        const track = webcamVideo.srcObject.getVideoTracks()[0];
                        if (track) {
                            console.log('Usando API ImageCapture para capturar foto');
                            const imageCapture = new ImageCapture(track);
                            
                            imageCapture.takePhoto()
                                .then(blob => {
                                    // Convertir blob a base64
                                    const reader = new FileReader();
                                    reader.onloadend = () => {
                                        const imageDataUrl = reader.result;
                                        
                                        // Mostrar imagen en visor principal
                                        updateCapturedImageDisplay(imageDataUrl);
                                        
                                        resolve(imageDataUrl);
                                    };
                                    reader.onerror = () => reject(new Error('Error al leer blob de imagen'));
                                    reader.readAsDataURL(blob);
                                })
                                .catch(err => {
                                    console.warn('Error al usar ImageCapture API, usando fallback:', err);
                                    // Fallback al método del canvas
                                    useFallbackCapture();
                                });
                                
                            return; // Importante: retornar para evitar ejecutar el método de fallback
                        }
                    } catch (err) {
                        console.warn('Error al configurar ImageCapture:', err);
                        // Continuar con método de fallback
                    }
                }
                
                // Método de fallback usando canvas
                useFallbackCapture();
                
                // Función para capturar con el método tradicional de canvas
                function useFallbackCapture() {
                    console.log('Usando método de canvas para capturar foto');
                    // Configurar canvas con dimensiones del video
                    canvas.width = webcamVideo.videoWidth;
                    canvas.height = webcamVideo.videoHeight;
                    
                    // Dibujar frame actual del video en el canvas
                    const context = canvas.getContext('2d');
                    context.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
                    
                    // Convertir a imagen
                    const imageDataUrl = canvas.toDataURL('image/jpeg');
                    
                    // Mostrar imagen
                    updateCapturedImageDisplay(imageDataUrl);
                    
                    // Retornar datos de imagen
                    resolve(imageDataUrl);
                }
                
                // Función auxiliar para actualizar la imagen en el visor
                function updateCapturedImageDisplay(imageDataUrl) {
                    const capturedImage = document.getElementById('captured-image');
                    const placeholder = document.getElementById('placeholder');
                    
                    if (capturedImage) {
                        capturedImage.src = imageDataUrl;
                        capturedImage.classList.remove('hidden');
                        if (placeholder) placeholder.classList.add('hidden');
                    }
                }
                
            } catch (error) {
                console.error('Error en captureImage:', error);
                reject(error);
            }
        });
    }
    
    /**
     * Añade una miniatura de imagen a la galería
     * @param {string} imageData - Imagen en formato base64
     */
    function addThumbnail(imageData) {
        if (!elements.thumbnailsGrid) return;
        
        // Crear elemento de miniatura
        const thumbnailDiv = document.createElement('div');
        thumbnailDiv.className = 'relative group';
        thumbnailDiv.dataset.index = capturedImages.length - 1;
        
        // Crear imagen
        const img = document.createElement('img');
        img.src = imageData;
        img.className = 'w-full h-16 object-cover rounded-sm border border-gray-200';
        img.alt = `Captura ${capturedImages.length}`;
        
        // Crear overlay para acciones
        const overlay = document.createElement('div');
        overlay.className = 'absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all rounded-sm flex items-center justify-center opacity-0 group-hover:opacity-100';
        
        // Crear botón de eliminar
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'bg-red-600 hover:bg-red-700 text-white p-1 rounded-full';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.addEventListener('click', function() {
            // Eliminar imagen del array
            const index = parseInt(thumbnailDiv.dataset.index);
            if (!isNaN(index) && index >= 0 && index < capturedImages.length) {
                capturedImages.splice(index, 1);
                
                // Eliminar miniatura
                thumbnailDiv.remove();
                
                // Actualizar índices de las miniaturas restantes
                const thumbnails = elements.thumbnailsGrid.querySelectorAll('[data-index]');
                thumbnails.forEach((thumb, i) => {
                    thumb.dataset.index = i;
                });
                
                // Actualizar contador
                if (elements.countDisplay) {
                    elements.countDisplay.textContent = `${capturedImages.length}/${targetCount}`;
                }
            }
        });
        
        // Añadir elementos
        overlay.appendChild(deleteBtn);
        thumbnailDiv.appendChild(img);
        thumbnailDiv.appendChild(overlay);
        elements.thumbnailsGrid.appendChild(thumbnailDiv);
    }
    
    /**
     * Actualiza la barra de progreso
     * @param {number} percent - Porcentaje de progreso (0-100)
     */
    function updateProgressBar(percent) {
        if (elements.progressBar) {
            elements.progressBar.style.width = `${percent}%`;
        }
        
        if (elements.countDisplay) {
            elements.countDisplay.textContent = `${currentCount}/${targetCount}`;
        }
    }
    
    /**
     * Reinicia la UI de captura automática
     */
    function resetAutoCaptureUI() {
        if (elements.startAutoBtn) {
            elements.startAutoBtn.innerHTML = '<i class="fas fa-bolt mr-2"></i> Iniciar captura automática';
            elements.startAutoBtn.classList.add('bg-gradient-to-r', 'from-blue-600', 'to-indigo-600', 'hover:from-blue-700', 'hover:to-indigo-700');
            elements.startAutoBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
        }
    }
    
    /**
     * Guarda todas las imágenes capturadas
     */
    async function saveAllCapturedImages() {
        if (!capturedImages.length) {
            showToast('No hay imágenes para guardar', 'info');
            return;
        }
        
        try {
            // Cambiar botón a estado de carga
            if (elements.saveAllBtn) {
                elements.saveAllBtn.disabled = true;
                elements.saveAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Guardando...';
            }
            
            // Obtener el ID de la mascota
            mascotaId = getMascotaId();
            
            if (!mascotaId) {
                showToast('Error: No se ha seleccionado una mascota', 'error');
                return;
            }
            
            let successCount = 0;
            let errorCount = 0;
            let validationErrors = [];  // Para acumular errores de validación
            
            // Guardar cada imagen por separado
            for (let i = 0; i < capturedImages.length; i++) {
                // Verificar si todavía tenemos espacio para más imágenes
                const currentCount = getCurrentImageCount() + successCount;
                if (currentCount >= 20) {
                    console.log(`Límite alcanzado durante el guardado (${currentCount}/20)`);
                    showToast(`Se alcanzó el límite de 20 imágenes. Se guardaron ${successCount} imágenes.`, 'warning');
                    break;
                }
                
                try {
                    await saveImage(capturedImages[i], mascotaId);
                    successCount++;
                } catch (err) {
                    console.error(`Error al guardar imagen ${i+1}:`, err);
                    errorCount++;
                    
                    // Si es un error de validación, guardar en lista
                    if (err.validation_error) {
                        validationErrors.push({
                            numero: i + 1,
                            mensaje: err.message,
                            objeto_detectado: err.objeto_detectado,
                            confianza: err.confianza
                        });
                        // No contar errores de validación para abortar (son errores del usuario, no del sistema)
                        errorCount--;
                    } else {
                        // Si hay demasiados errores del sistema, abortar
                        if (errorCount > 3) {
                            showToast('Demasiados errores al guardar imágenes, proceso abortado', 'error');
                            break;
                        }
                    }
                }
                
                // Actualizar barra de progreso
                updateProgressBar((i + 1) / capturedImages.length * 100);
            }
            
            // Limpiar imágenes guardadas
            capturedImages = [];
            if (elements.thumbnailsGrid) {
                elements.thumbnailsGrid.innerHTML = '';
            }
            
            // Ocultar contenedor de miniaturas
            if (elements.thumbnailsContainer) {
                elements.thumbnailsContainer.classList.add('hidden');
            }
            
            // Mostrar resultado final
            if (successCount > 0 && validationErrors.length > 0) {
                // Hay imágenes guardadas Y rechazadas - mostrar ambas
                showToast(`${successCount} imágenes guardadas, ${validationErrors.length} rechazadas`, 'warning');
                
                // Mostrar detalle de imágenes rechazadas
                if (typeof Swal !== 'undefined') {
                    const erroresHTML = validationErrors.map(err => `
                        <div class="text-left bg-orange-50 border-l-4 border-orange-400 p-2 rounded mb-2">
                            <p class="text-sm font-semibold text-gray-800">Imagen ${err.numero}</p>
                            <p class="text-xs text-gray-700">
                                <strong>Detectado:</strong> ${err.objeto_detectado}<br>
                                <strong>Confianza:</strong> ${err.confianza ? err.confianza.toFixed(1) + '%' : 'N/A'}
                            </p>
                        </div>
                    `).join('');
                    
                    Swal.fire({
                        icon: 'warning',
                        title: '⚠️ Algunas imágenes fueron rechazadas',
                        html: `
                            <div class="space-y-2">
                                <p class="text-sm text-green-700 mb-2">
                                    ✅ <strong>${successCount} imagen${successCount > 1 ? 'es' : ''} guardada${successCount > 1 ? 's' : ''} correctamente</strong>
                                </p>
                                <p class="text-sm text-gray-700 mb-3">
                                    ❌ Las siguientes imágenes no fueron aceptadas porque no contienen caninos válidos:
                                </p>
                                ${erroresHTML}
                                <div class="bg-blue-50 border-l-4 border-blue-400 p-3 rounded mt-3">
                                    <p class="text-xs text-blue-800">
                                        <strong>💡 Tip:</strong> Solo se aceptan imágenes claras de perros. 
                                        Intenta capturar con mejor iluminación y ángulo.
                                    </p>
                                </div>
                            </div>
                        `,
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#3B82F6',
                        width: '600px',
                        allowOutsideClick: false
                    }).then(() => {
                        // Recargar DESPUÉS de cerrar el modal
                        window.location.reload();
                    });
                } else {
                    // Sin SweetAlert, recargar con delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 2500);
                }
            } else if (successCount > 0) {
                // Solo imágenes guardadas correctamente
                showToast(`${successCount} imágenes guardadas correctamente`, 'success');
                
                // Recargar la página para actualizar todo
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else if (validationErrors.length > 0) {
                // Solo hubo errores de validación, ninguna guardada
                showToast('Ninguna imagen fue aceptada. Por favor, captura imágenes de perros.', 'error');
                
                // Mostrar detalle
                if (typeof Swal !== 'undefined') {
                    const erroresHTML = validationErrors.map(err => `
                        <div class="text-left bg-orange-50 border-l-4 border-orange-400 p-2 rounded mb-2">
                            <p class="text-sm font-semibold text-gray-800">Imagen ${err.numero}</p>
                            <p class="text-xs text-gray-700">
                                <strong>Detectado:</strong> ${err.objeto_detectado}<br>
                                <strong>Confianza:</strong> ${err.confianza ? err.confianza.toFixed(1) + '%' : 'N/A'}
                            </p>
                        </div>
                    `).join('');
                    
                    Swal.fire({
                        icon: 'error',
                        title: '❌ Todas las imágenes fueron rechazadas',
                        html: `
                            <div class="space-y-2">
                                <p class="text-sm text-gray-700 mb-3">
                                    Ninguna imagen fue aceptada porque no contienen caninos válidos:
                                </p>
                                ${erroresHTML}
                                <div class="bg-blue-50 border-l-4 border-blue-400 p-3 rounded mt-3">
                                    <p class="text-xs text-blue-800">
                                        <strong>💡 Recomendación:</strong> Captura imágenes claras de perros. 
                                        Verifica que el animal esté bien iluminado y enfocado.
                                    </p>
                                </div>
                            </div>
                        `,
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#3B82F6',
                        width: '600px'
                    });
                }
            }
            
            // Verificar límite alcanzado (solo si se guardaron imágenes)
            if (successCount > 0) {
                const biometriaContent = document.querySelector('.biometria-content');
                if (biometriaContent) {
                    const imagesCountText = biometriaContent.querySelector('.text-gray-800.font-bold');
                    if (imagesCountText) {
                        const countMatch = imagesCountText.textContent.match(/(\d+)\s*\/\s*20/);
                        if (countMatch && parseInt(countMatch[1]) >= 20) {
                            disableCaptureInterface('Has alcanzado el límite de 20 imágenes biométricas para esta mascota.');
                        }
                    }
                }
            }
            
            if (errorCount > 0) {
                showToast(`No se pudieron guardar ${errorCount} imágenes (errores de sistema)`, 'warning');
            }
        } catch (err) {
            console.error('Error al guardar imágenes:', err);
            showToast('Error al guardar las imágenes', 'error');
        } finally {
            // Restaurar botón
            if (elements.saveAllBtn) {
                elements.saveAllBtn.disabled = false;
                elements.saveAllBtn.innerHTML = '<i class="fas fa-save mr-1"></i> Guardar todas';
            }
        }
    }
    
    /**
     * Guarda una imagen en el servidor
     * @param {string} imageData - Imagen en formato base64
     * @param {string} mascotaId - ID de la mascota
     * @returns {Promise} - Promise con el resultado de la operación
     */
    function saveImage(imageData, mascotaId) {
        return new Promise(async (resolve, reject) => {
            try {
                // Crear FormData
                const formData = new FormData();
                formData.append('imagen_base64', imageData);
                formData.append('mascota_id', mascotaId);
                formData.append('tipo', 'biometrica');
                
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
                        // Actualizar barra de progreso si existe
                        updateProgressBar(data.images_count, 20);
                        resolve(data);
                    } else {
                        // Verificar si es un error de validación canina
                        if (data.validation_error && data.details) {
                            // Error de validación - imagen no es de un perro
                            reject({
                                validation_error: true,
                                message: data.details.mensaje || 'La imagen no contiene un canino válido',
                                objeto_detectado: data.details.objeto_detectado,
                                confianza: data.details.confianza,
                                recomendacion: data.details.recomendacion
                            });
                        } else {
                            // Otro tipo de error
                            reject(new Error(data.error || 'Error al guardar la imagen'));
                        }
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    
                    // Verificar si es error de validación incluso con status error
                    if (errorData.validation_error && errorData.details) {
                        reject({
                            validation_error: true,
                            message: errorData.details.mensaje || 'La imagen no contiene un canino válido',
                            objeto_detectado: errorData.details.objeto_detectado,
                            confianza: errorData.details.confianza,
                            recomendacion: errorData.details.recomendacion
                        });
                    } else {
                        reject(new Error(`Error ${response.status}: No se pudo guardar la imagen`));
                    }
                }
            } catch (err) {
                reject(err);
            }
        });
    }
    
    /**
     * Obtiene el ID de la mascota desde múltiples fuentes posibles
     * @returns {string|null} - ID de la mascota o null si no se encuentra
     */
    function getMascotaId() {
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
        
        return mascotaId;
    }
    
    // Obtener el CSRF token para las solicitudes AJAX
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    /**
     * Muestra una notificación tipo toast
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de mensaje (success, error, warning, info)
     */
    function showToast(message, type = 'info') {
        // Verificar si está disponible la función global
        if (window.showToast) {
            window.showToast(message, type);
        } 
        // Si no está disponible, verificar si está SweetAlert2
        else if (window.Swal) {
            Swal.fire({
                text: message,
                icon: type,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true
            });
        }
        // Si nada está disponible, usar un alert simple
        else {
            alert(message);
        }
        
        // También logueamos para depuración
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    /**
     * Muestra un mensaje de error específico para validación canina
     * @param {object} details - Detalles del error de validación
     */
    function showValidationError(details) {
        const mensaje = details.mensaje || 'La imagen no contiene un canino válido';
        const objetoDetectado = details.objeto_detectado || 'Desconocido';
        const confianza = details.confianza || 0;
        const recomendacion = details.recomendacion || 'Por favor, sube una imagen clara de un perro.';
        
        // Intentar usar SweetAlert2 si está disponible
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: '🐕 Imagen no válida',
                html: `
                    <div class="text-left space-y-3">
                        <div class="bg-orange-50 border-l-4 border-orange-400 p-3 rounded">
                            <p class="text-sm text-gray-800 mb-2">
                                <strong>❌ ${mensaje}</strong>
                            </p>
                            <div class="text-xs text-gray-700 space-y-1">
                                <p><strong>Detectado:</strong> ${objetoDetectado}</p>
                                <p><strong>Confianza:</strong> ${confianza.toFixed(1)}%</p>
                            </div>
                        </div>
                        <div class="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
                            <p class="text-xs text-blue-800">
                                <strong>💡 Recomendación:</strong><br>
                                ${recomendacion}
                            </p>
                        </div>
                    </div>
                `,
                confirmButtonText: 'Entendido',
                confirmButtonColor: '#3B82F6',
                width: '500px'
            });
        } else {
            // Fallback: usar mensaje simple
            const mensajeCompleto = `
❌ Imagen no válida

${mensaje}

🔍 Detectado: ${objetoDetectado}
📊 Confianza: ${confianza.toFixed(1)}%

💡 ${recomendacion}
            `.trim();
            
            showToast(mensajeCompleto, 'warning');
        }
        
        console.warn('Validación canina falló:', {
            mensaje,
            objetoDetectado,
            confianza,
            recomendacion
        });
    }
    
    /**
     * Comprueba manualmente el estado de la cámara y actualiza el botón
     * Esta función puede ser llamada desde fuera cuando se sabe que el estado ha cambiado
     */
    function checkCameraStateAndUpdateButton() {
        console.log('Verificando estado de cámara manualmente...');
        if (!elements.startAutoBtn) {
            console.log('El botón de captura automática no está disponible');
            return;
        }
        
        // Verificar estado de la cámara usando la variable global
        const isCameraActive = window.biometricCameraActive === true;
        console.log('Estado actual de la cámara según variable global:', isCameraActive);
        
        // También podemos verificar por el video directamente
        const webcamVideo = document.getElementById('webcam');
        const hasVideoStream = webcamVideo && webcamVideo.srcObject;
        console.log('Tiene stream de video:', !!hasVideoStream);
        
        if (isCameraActive || hasVideoStream) {
            console.log('Habilitando botón de captura automática (verificación manual)');
            elements.startAutoBtn.disabled = false;
        } else {
            console.log('Deshabilitando botón de captura automática (verificación manual)');
            elements.startAutoBtn.disabled = true;
        }
    }
    
    // API pública
    return {
        init,
        startAutoCapture,
        stopAutoCapture,
        saveAllCapturedImages,
        checkCameraStateAndUpdateButton
    };
})();

// Función para inicializar el módulo con reintento
window.initWithRetry = function() {
    // Verificar si estamos en la página de biometría
    if (document.querySelector('.biometria-content')) {
        console.log('Intentando inicializar módulo de captura automática...');
        
        // Primero intentamos inicializar
        window.BiometriaCapturaAutomatica.init();
        
        // Verificar explícitamente si la cámara ya está activa
        if (window.biometricCameraActive === true) {
            console.log('Cámara ya está activa, asegurando que el botón esté habilitado');
            const startAutoBtn = document.getElementById('start-auto-capture');
            if (startAutoBtn) {
                console.log('Encontrado botón de captura automática, habilitando...');
                startAutoBtn.disabled = false;
            }
        }
        
        // Añadir validación en tiempo real al campo de número de capturas
        const countInput = document.getElementById('auto-capture-count');
        if (countInput) {
            countInput.addEventListener('change', function(e) {
                const currentImages = getCurrentImageCount();
                const remainingImages = 20 - currentImages;
                
                // Asegurar que el valor esté entre 1 y el máximo permitido
                if (this.value > remainingImages) {
                    this.value = remainingImages;
                    showToast(`El número máximo permitido es ${remainingImages}`, 'info');
                } else if (this.value < 1) {
                    this.value = 1;
                }
            });
        }
        // El botón de forzar habilitación ha sido eliminado ya que ahora la activación es automática
        
        // Verificamos si los elementos esenciales ahora existen
        const startAutoBtn = document.getElementById('start-auto-capture');
        const progressContainer = document.getElementById('auto-capture-progress');
        
        // Si hay una mascota seleccionada pero no encontramos los elementos, podría ser un problema de timing
        const biometriaContent = document.querySelector('.biometria-content');
        const hasMascotaSelected = biometriaContent && biometriaContent.getAttribute('data-mascota-id');
        
        if (hasMascotaSelected && (!startAutoBtn || !progressContainer)) {
            console.log('Elementos no encontrados en primer intento, reintentando en 1 segundo...');
            // Reintentamos después de un segundo
            setTimeout(function() {
                BiometriaCapturaAutomatica.init();
            }, 1000);
        }
    }
}

// Inicializar módulo cuando el documento esté listo
document.addEventListener('DOMContentLoaded', initWithRetry);

// Reinicializar cuando se cargue el contenido biométrico por AJAX
document.addEventListener('biometriaContentLoaded', function() {
    console.log('Evento biometriaContentLoaded detectado, inicializando módulo de captura automática...');
    // Esperamos un poco para asegurar que el DOM se ha actualizado
    setTimeout(initWithRetry, 800);
});

// También intentamos inicializar cuando se selecciona una pestaña (podría ser la de biometría)
document.addEventListener('click', function(event) {
    if (event.target && event.target.classList && event.target.classList.contains('tab-btn')) {
        console.log('Cambio de pestaña detectado, verificando si es biometría...');
        setTimeout(initWithRetry, 500);
    }
});