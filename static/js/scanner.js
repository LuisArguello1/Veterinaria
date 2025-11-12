document.addEventListener('DOMContentLoaded', function() {
        initScanner();
        initScannerTabs();
        
        // Verificamos si estamos en la página de escáner con la pestaña de datos biométricos activa
        const biometriaContent = document.querySelector('.biometria-content');
        if (biometriaContent && !document.getElementById('mascota-selector-container')) {
            // Solo inicializamos el selector de mascotas si no existe ya
            if (typeof initMascotaSelector === 'function') {
                initMascotaSelector();
            }
        }
    });
    
    // Variable global para el estado de la cámara
    let scannerCameraActive = false;
    
    // Función para verificar y corregir el estado de la cámara
    function verificarEstadoCamera() {
        const webcamVideo = document.getElementById('scanner-webcam');
        const startCameraBtn = document.getElementById('scanner-start-camera');
        
        const tieneVideo = webcamVideo && webcamVideo.srcObject;
        
        if (scannerCameraActive && !tieneVideo) {
            // Estado inconsistente: dice que está activa pero no hay video
            console.log('Corrigiendo estado inconsistente: activa->inactiva');
            scannerCameraActive = false;
            if (startCameraBtn) {
                startCameraBtn.innerHTML = '<i class="fas fa-play mr-2"></i> Iniciar cámara';
                startCameraBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
                startCameraBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
            }
        } else if (!scannerCameraActive && tieneVideo) {
            // Estado inconsistente: dice que está inactiva pero hay video
            console.log('Corrigiendo estado inconsistente: inactiva->activa');
            scannerCameraActive = true;
            if (startCameraBtn) {
                startCameraBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> Detener cámara';
                startCameraBtn.classList.remove('bg-primary-600', 'hover:bg-primary-700');
                startCameraBtn.classList.add('bg-red-600', 'hover:bg-red-700');
            }
        }
        
        return scannerCameraActive;
    }
    
    function initScannerTabs() {
        const tabButtons = document.querySelectorAll('.scan-tab-btn');
        const tabContents = document.querySelectorAll('.scan-tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const target = button.dataset.target;
                
                // Actualizar botones
                tabButtons.forEach(btn => {
                    btn.classList.remove('active', 'bg-white', 'shadow-sm');
                    btn.classList.add('text-gray-700', 'hover:text-gray-900');
                });
                
                button.classList.add('active', 'bg-white', 'shadow-sm');
                button.classList.remove('text-gray-700', 'hover:text-gray-900');
                
                // Actualizar contenidos
                tabContents.forEach(content => {
                    content.classList.add('hidden');
                });
                
                document.getElementById(target).classList.remove('hidden');
                
                // Detener cámara si se cambia de pestaña
                if (target !== 'camera-tab') {
                    window.stopScannerCamera();
                }
            });
        });
    }
    
    // Función global para detener la cámara (accesible desde otras partes)
    window.stopScannerCamera = function() {
        const webcamVideo = document.getElementById('scanner-webcam');
        const startCameraBtn = document.getElementById('scanner-start-camera');
        const capturePhotoBtn = document.getElementById('scanner-capture-photo');
        const cameraOverlay = document.getElementById('scanner-camera-overlay');
        const cameraSelectContainer = document.getElementById('scanner-camera-select-container');
        
        console.log('stopScannerCamera global llamada, estado previo:', scannerCameraActive);
        
        if (webcamVideo && webcamVideo.srcObject) {
            const tracks = webcamVideo.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            webcamVideo.srcObject = null;
        }
        
        // Marcar cámara como inactiva globalmente
        scannerCameraActive = false;
        console.log('Cámara detenida globalmente, nuevo estado:', scannerCameraActive);
        
        // Restaurar botón de iniciar cámara
        if (startCameraBtn) {
            startCameraBtn.innerHTML = '<i class="fas fa-play mr-2"></i> Iniciar cámara';
            startCameraBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
            startCameraBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
        }
        
        // Deshabilitar botón de captura
        if (capturePhotoBtn) {
            capturePhotoBtn.disabled = true;
        }
        
        // Ocultar selector de cámaras
        if (cameraSelectContainer) {
            cameraSelectContainer.style.display = 'none';
        }
        
        // Mostrar overlay inicial
        if (cameraOverlay) {
            cameraOverlay.innerHTML = '<i class="fas fa-video mr-2"></i> Presiona "Iniciar cámara" para comenzar';
            cameraOverlay.classList.remove('hidden');
        }
    };

    function initScanner() {
        // Variables de la cámara
        const startCameraBtn = document.getElementById('scanner-start-camera');
        const capturePhotoBtn = document.getElementById('scanner-capture-photo');
        const webcamVideo = document.getElementById('scanner-webcam');
        const canvas = document.getElementById('scanner-canvas');
        const cameraOverlay = document.getElementById('scanner-camera-overlay');
        const cameraSelectContainer = document.getElementById('scanner-camera-select-container');
        const cameraSelect = document.getElementById('scanner-camera-select');
        const switchCameraBtn = document.getElementById('scanner-switch-camera');
        let stream = null;
        let currentDeviceId = '';
        let capturedImageData = null; // Variable para guardar la imagen capturada
        // Eliminamos la variable local cameraActive ya que usamos la global scannerCameraActive
        
        // Variables de vista previa de cámara
        const cameraPreview = document.getElementById('scanner-camera-preview');
        const cameraPreviewImg = document.getElementById('scanner-camera-preview-img');
        const clearCameraPhotoBtn = document.getElementById('scanner-clear-camera-photo');
        const retakePhotoBtn = document.getElementById('scanner-retake-photo');
        const recognizePhotoBtn = document.getElementById('scanner-recognize-photo');
        
        // Variables de subida de archivos
        const fileInput = document.getElementById('scanner-file-input');
        const selectFileBtn = document.getElementById('scanner-select-file-btn');
        const uploadFileBtn = document.getElementById('scanner-upload-file-btn');
        const filePreview = document.getElementById('scanner-file-preview');
        const previewImg = document.getElementById('scanner-preview-img');
        const clearFileBtn = document.getElementById('scanner-clear-file');
        const dropZone = document.getElementById('scanner-drop-zone');
        
        // Variables de resultados
        const recognitionResult = document.getElementById('recognition-result');
        const resultLoading = document.getElementById('result-loading');
        const resultSuccess = document.getElementById('result-success');
        
        // Variables para predicciones de IA
        const aiPredictionsPanel = document.getElementById('ai-predictions');
        const aiPredictionsLoading = document.getElementById('ai-predictions-loading');
        const aiPredictionsContent = document.getElementById('ai-predictions-content');
        const resultError = document.getElementById('result-error');
        
        // Verificar si están deshabilitados los botones
        const disabled = startCameraBtn.disabled;
        
        // Función para obtener dispositivos de cámara disponibles
        async function getCameraDevices() {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                
                // Limpiar selector
                cameraSelect.innerHTML = '';
                
                // Si no hay dispositivos
                if (videoDevices.length === 0) {
                    const option = document.createElement('option');
                    option.text = 'No se encontraron cámaras';
                    option.value = '';
                    cameraSelect.add(option);
                    switchCameraBtn.disabled = true;
                    return;
                }
                
                // Agregar opciones al selector
                videoDevices.forEach((device, index) => {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.text = device.label || `Cámara ${index + 1}`;
                    cameraSelect.add(option);
                });
                
                // Habilitar botón de cambio si hay más de una cámara
                switchCameraBtn.disabled = videoDevices.length <= 1;
                
                return videoDevices;
            } catch (err) {
                console.error('Error al enumerar dispositivos:', err);
                return [];
            }
        }
        
        // Función para iniciar la cámara con un dispositivo específico
        async function startCamera(deviceId = null) {
            try {
                // Mostrar overlay de inicialización
                cameraOverlay.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Inicializando cámara...';
                cameraOverlay.classList.remove('hidden');
                
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
                } else {
                    // De lo contrario, preferir cámara trasera en móviles
                    constraints.video.facingMode = { ideal: 'environment' };
                }
                
                // Solicitar acceso a la cámara
                stream = await navigator.mediaDevices.getUserMedia(constraints);
                
                // Asignar stream al elemento video
                webcamVideo.srcObject = stream;
                await webcamVideo.play();
                
                // Obtener dispositivos después de obtener permisos
                const devices = await getCameraDevices();
                
                // Mostrar selector de cámaras si hay dispositivos
                if (devices && devices.length > 0) {
                    cameraSelectContainer.style.display = 'block';
                    
                    // Actualizar deviceId actual si no se proporcionó uno
                    if (!deviceId) {
                        const track = stream.getVideoTracks()[0];
                        const settings = track.getSettings();
                        currentDeviceId = settings.deviceId;
                        
                        // Seleccionar el dispositivo actual en el selector
                        if (currentDeviceId) {
                            cameraSelect.value = currentDeviceId;
                        }
                    }
                }
                    
                // Habilitar botón de captura
                capturePhotoBtn.disabled = false;
                
                // Cambiar estado del botón de iniciar cámara
                startCameraBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> Detener cámara';
                startCameraBtn.classList.remove('bg-primary-600', 'hover:bg-primary-700');
                startCameraBtn.classList.add('bg-red-600', 'hover:bg-red-700');
                
                // Ocultar overlay cuando la cámara esté lista
                cameraOverlay.classList.add('hidden');
                
                // Marcar cámara como activa
                scannerCameraActive = true;
                console.log('Cámara iniciada, estado:', scannerCameraActive);
                
                return true;
            } catch (err) {
                console.error('Error al acceder a la cámara:', err);
                alert('No se pudo acceder a la cámara. Por favor, verifica que has concedido permisos.');
                cameraOverlay.innerHTML = '<i class="fas fa-video-slash mr-2"></i> Error al inicializar cámara. Presiona "Iniciar cámara" para reintentar.';
                scannerCameraActive = false; // Asegurar que el estado sea correcto
                return false;
            }
        }
        
        // Inicializar cámara
        if (startCameraBtn && !disabled) {
            startCameraBtn.addEventListener('click', async () => {
                // Verificar estado antes de decidir qué hacer
                const estadoActual = verificarEstadoCamera();
                console.log('Botón clickeado, estado verificado:', estadoActual);
                
                if (estadoActual) {
                    // Si la cámara está activa, detenerla
                    console.log('Deteniendo cámara...');
                    stopScannerCamera();
                } else {
                    // Si la cámara no está activa, iniciarla
                    console.log('Iniciando cámara...');
                    await startCamera();
                }
            });
        }
        
        // Manejar cambio de cámara desde el selector
        if (cameraSelect) {
            cameraSelect.addEventListener('change', async () => {
                const selectedDeviceId = cameraSelect.value;
                if (selectedDeviceId && selectedDeviceId !== currentDeviceId) {
                    // Detener cámara actual
                    stopScannerCamera();
                    // Iniciar con nueva cámara
                    await startCamera(selectedDeviceId);
                }
            });
        }
        
        // Botón para cambiar cámara rápidamente
        if (switchCameraBtn) {
            switchCameraBtn.addEventListener('click', async () => {
                // Si no hay un select válido, no hacer nada
                if (!cameraSelect || cameraSelect.options.length <= 1) {
                    return;
                }
                
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
                const selectedDeviceId = cameraSelect.value;
                
                // Cambiar cámara
                stopScannerCamera();
                await startCamera(selectedDeviceId);
            });
        }
        
        // Capturar foto
        if (capturePhotoBtn) {
            capturePhotoBtn.addEventListener('click', () => {
                if (!stream) return;
                
                console.log('Capturando foto, estado antes:', scannerCameraActive);
                
                // Verificar que el video tenga dimensiones válidas
                if (webcamVideo.videoWidth === 0 || webcamVideo.videoHeight === 0) {
                    console.error('Video sin dimensiones válidas');
                    alert('Error al capturar la foto. Por favor, intenta de nuevo.');
                    return;
                }
                
                // Configurar canvas con dimensiones del video
                canvas.width = webcamVideo.videoWidth;
                canvas.height = webcamVideo.videoHeight;
                
                console.log('Dimensiones del canvas:', canvas.width, 'x', canvas.height);
                
                // Dibujar frame actual del video en el canvas
                const context = canvas.getContext('2d');
                context.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
                
                // Obtener imagen como base64 comprimida (calidad 0.8 para reducir tamaño)
                capturedImageData = canvas.toDataURL('image/jpeg', 0.8);
                
                console.log('Imagen capturada, tamaño:', capturedImageData.length, 'caracteres');
                
                // Verificar que la imagen se capturó correctamente
                if (!capturedImageData || capturedImageData.length < 1000) {
                    console.error('Imagen capturada inválida o vacía');
                    alert('Error al capturar la foto. Por favor, intenta de nuevo.');
                    return;
                }
                
                // Detener cámara
                stopScannerCamera();
                
                // LUEGO mostrar vista previa de la foto capturada
                setTimeout(() => {
                    if (cameraPreview && cameraPreviewImg && capturedImageData) {
                        console.log('Mostrando vista previa de la imagen...');
                        
                        // IMPORTANTE: Limpiar la imagen anterior primero
                        cameraPreviewImg.src = '';
                        cameraPreviewImg.removeAttribute('src');
                        
                        // Forzar un pequeño delay para asegurar que se limpia
                        setTimeout(() => {
                            // Configurar eventos de carga
                            cameraPreviewImg.onload = () => {
                                console.log('✅ Imagen cargada exitosamente en el preview');
                            };
                            
                            cameraPreviewImg.onerror = (error) => {
                                console.error('❌ Error al cargar la imagen en el preview:', error);
                                console.log('Longitud de datos:', capturedImageData.length);
                                console.log('Primeros 100 caracteres:', capturedImageData.substring(0, 100));
                            };
                            
                            // Asignar la nueva imagen
                            cameraPreviewImg.src = capturedImageData;
                            cameraPreview.classList.remove('hidden');
                            
                            // Hacer scroll a la vista previa
                            cameraPreview.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }, 50);
                    } else {
                        console.error('Elementos de preview no encontrados');
                    }
                }, 200);
            });
        }
        
        // Botón para reconocer la foto capturada
        if (recognizePhotoBtn) {
            recognizePhotoBtn.addEventListener('click', () => {
                if (capturedImageData) {
                    // Ocultar vista previa
                    if (cameraPreview) {
                        cameraPreview.classList.add('hidden');
                    }
                    // Procesar reconocimiento
                    processRecognition(capturedImageData);
                }
            });
        }
        
        // Botón para limpiar/cancelar la foto capturada
        if (clearCameraPhotoBtn) {
            clearCameraPhotoBtn.addEventListener('click', () => {
                console.log('❌ Cancelando foto capturada...');
                
                capturedImageData = null;
                
                // Limpiar COMPLETAMENTE la imagen de preview
                if (cameraPreviewImg) {
                    cameraPreviewImg.onload = null;
                    cameraPreviewImg.onerror = null;
                    cameraPreviewImg.src = '';
                    cameraPreviewImg.removeAttribute('src');
                }
                
                if (cameraPreview) {
                    cameraPreview.classList.add('hidden');
                }
                
                console.log('✅ Foto cancelada y limpiada');
            });
        }
        
        // Botón para tomar otra foto
        if (retakePhotoBtn) {
            retakePhotoBtn.addEventListener('click', async () => {
                console.log('🔄 Retomando foto...');
                
                // Limpiar imagen capturada
                capturedImageData = null;
                
                // Limpiar COMPLETAMENTE la imagen de preview
                if (cameraPreviewImg) {
                    cameraPreviewImg.onload = null;
                    cameraPreviewImg.onerror = null;
                    cameraPreviewImg.src = '';
                    cameraPreviewImg.removeAttribute('src');
                    console.log('🧹 Imagen de preview limpiada');
                }
                
                // Ocultar vista previa
                if (cameraPreview) {
                    cameraPreview.classList.add('hidden');
                    console.log('👁️ Vista previa ocultada');
                }
                
                // Ocultar resultados si están visibles
                if (recognitionResult) {
                    recognitionResult.classList.add('hidden');
                }
                
                // Hacer scroll de vuelta al área de la cámara
                const cameraTab = document.getElementById('camera-tab');
                if (cameraTab) {
                    cameraTab.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                
                // Esperar un momento antes de reiniciar la cámara
                await new Promise(resolve => setTimeout(resolve, 400));
                
                // Reiniciar cámara
                console.log('📹 Reiniciando cámara con deviceId:', currentDeviceId);
                await startCamera(currentDeviceId || null);
                console.log('✅ Cámara reiniciada');
            });
        }
        
        
        // Subida de archivos
        if (selectFileBtn && !disabled) {
            selectFileBtn.addEventListener('click', () => {
                fileInput.click();
            });
        }
        
        // Manejar selección de archivos
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                handleFileSelect(e.target.files);
            });
        }
        
        // Manejar arrastrar y soltar
        if (dropZone && !disabled) {
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
                        if (files.length > 0) {
                            fileInput.files = files;
                            handleFileSelect(files);
                        }
                    }
                }, false);
            });
        }
        
        // Manejar subida de archivo para reconocimiento
        if (uploadFileBtn) {
            uploadFileBtn.addEventListener('click', () => {
                if (fileInput.files && fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = (e) => {
                        processRecognition(e.target.result);
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
        }
        
        // Limpiar archivo
        if (clearFileBtn) {
            clearFileBtn.addEventListener('click', () => {
                fileInput.value = '';
                filePreview.classList.add('hidden');
                uploadFileBtn.disabled = true;
            });
        }
        
        // Función para detener la cámara (usa la función global)
        function stopScannerCamera() {
            // Usar la función global para mantener consistencia
            window.stopScannerCamera();
            
            // También limpiar las variables locales
            if (stream) {
                stream = null;
            }
        }
        
        // Función para manejar archivo seleccionado
        function handleFileSelect(files) {
            if (files && files.length > 0) {
                const file = files[0];
                
                // ✅ VALIDACIÓN: Verificar tipo de archivo
                if (!file.type.startsWith('image/')) {
                    Swal.fire({
                        title: 'Archivo no válido',
                        text: 'Por favor, selecciona una imagen válida (JPG, PNG, etc.)',
                        icon: 'error',
                        confirmButtonColor: '#EF4444'
                    });
                    return;
                }
                
                // ✅ VALIDACIÓN: Verificar tamaño máximo (5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB en bytes
                if (file.size > maxSize) {
                    Swal.fire({
                        title: 'Imagen demasiado grande',
                        text: `La imagen no puede ser mayor a 5MB. Tamaño actual: ${(file.size / 1024 / 1024).toFixed(2)}MB`,
                        icon: 'error',
                        confirmButtonColor: '#EF4444'
                    });
                    return;
                }
                
                const reader = new FileReader();
                
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    filePreview.classList.remove('hidden');
                    uploadFileBtn.disabled = false;
                };
                
                reader.readAsDataURL(file);
            }
        }
        
        // Función para procesar reconocimiento
        async function processRecognition(imageData) {
            try {
                // Guardar imagen para reportes posteriores
                lastCapturedImage = imageData;
                console.log('📸 Imagen guardada para posibles reportes');
                
                // Obtener referencias a los elementos de UI
                const recognitionResult = document.getElementById('recognition-result');
                const resultLoading = document.getElementById('result-loading');
                const resultSuccess = document.getElementById('result-success');
                const resultError = document.getElementById('result-error');
                
                // Mostrar sección de resultados
                if (recognitionResult) recognitionResult.classList.remove('hidden');
                if (resultLoading) resultLoading.classList.remove('hidden');
                if (resultSuccess) resultSuccess.classList.add('hidden');
                if (resultError) resultError.classList.add('hidden');
                
                // Hacer scroll a la sección de resultados
                recognitionResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Comprimir imagen antes de enviar
                const compressedImageData = await compressImage(imageData, 800, 600, 0.85);
                
                // Crear FormData para enviar la imagen
                const formData = new FormData();
                formData.append('imagen_base64', compressedImageData);
                
                // Realizar la petición
                const response = await fetch('/scanner/upload-recognition/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                // Procesar respuesta
                const data = await response.json();
                
                if (data.success) {
                    // Ocultar cargando
                    resultLoading.classList.add('hidden');
                    
                    const reconocimiento = data.reconocimiento;
                    
                    if (reconocimiento.exito) {
                        // Mostrar resultado exitoso
                        resultSuccess.classList.remove('hidden');
                        
                        const mascota = data.mascota;
                        const propietario = data.propietario;
                        
                        // Actualizar información principal de la mascota
                        document.getElementById('result-nombre').textContent = mascota.nombre || 'Sin nombre';
                        
                        // Solo raza (sin especie)
                        const razaTexto = mascota.raza || 'Sin raza específica';
                        document.getElementById('result-raza').querySelector('span').textContent = razaTexto;
                        
                        // Edad y peso
                        const edadTexto = mascota.edad ? `${mascota.edad} años` : 'Edad desconocida';
                        const pesoTexto = mascota.peso ? `${mascota.peso} kg` : 'Peso no registrado';
                        document.getElementById('result-edad-peso').querySelector('span').textContent = `${edadTexto} • ${pesoTexto}`;
                        
                        // Foto de la mascota
                        const fotoMascota = document.getElementById('result-foto-mascota');
                        const iconoMascota = document.getElementById('result-icono-mascota');
                        if (mascota.foto_perfil) {
                            fotoMascota.src = mascota.foto_perfil;
                            fotoMascota.classList.remove('hidden');
                            iconoMascota.classList.add('hidden');
                        } else {
                            fotoMascota.classList.add('hidden');
                            iconoMascota.classList.remove('hidden');
                        }
                        
                        // Información del propietario
                        if (propietario) {
                            document.getElementById('result-propietario-nombre').textContent = propietario.nombre_completo || 'Sin nombre';
                            document.getElementById('result-propietario-email').querySelector('span').textContent = propietario.email || 'Sin email';
                            document.getElementById('result-propietario-telefono').querySelector('span').textContent = propietario.telefono || 'Sin teléfono';
                            
                            // Foto del propietario
                            const fotoPropietario = document.getElementById('result-foto-propietario');
                            const iconoPropietario = document.getElementById('result-icono-propietario');
                            if (propietario.foto_perfil) {
                                fotoPropietario.src = propietario.foto_perfil;
                                fotoPropietario.classList.remove('hidden');
                                iconoPropietario.classList.add('hidden');
                            } else {
                                fotoPropietario.classList.add('hidden');
                                iconoPropietario.classList.remove('hidden');
                            }
                        } else {
                            document.getElementById('result-propietario-nombre').textContent = 'Sin propietario registrado';
                            document.getElementById('result-propietario-email').querySelector('span').textContent = '-';
                            document.getElementById('result-propietario-telefono').querySelector('span').textContent = '-';
                        }
                        
                        // Detalles adicionales (sin microchip)
                        document.getElementById('result-color').textContent = mascota.color || '-';
                        document.getElementById('result-genero').textContent = mascota.genero || '-';
                        document.getElementById('result-etapa-vida').textContent = mascota.etapa_vida || '-';
                        document.getElementById('result-estado-salud').textContent = mascota.estado_salud || 'Normal';
                        
                        // Confianza y tiempo
                        document.getElementById('result-confianza').textContent = `Confianza: ${(reconocimiento.confianza * 100).toFixed(1)}%`;
                        document.getElementById('result-tiempo').textContent = `${reconocimiento.tiempo_procesamiento?.toFixed(2) || '0.00'}s`;
                        
                        // Actualizar clases de confianza
                        const confianzaElement = document.getElementById('result-confianza');
                        confianzaElement.className = 'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium';
                        
                        if (reconocimiento.confianza >= 0.9) {
                            confianzaElement.classList.add('bg-green-100', 'text-green-800');
                        } else if (reconocimiento.confianza >= 0.7) {
                            confianzaElement.classList.add('bg-blue-100', 'text-blue-800');
                        } else {
                            confianzaElement.classList.add('bg-yellow-100', 'text-yellow-800');
                        }
                        
                        // Mensaje de éxito personalizado
                        const mensajeElement = document.getElementById('result-success-message');
                        mensajeElement.textContent = reconocimiento.mensaje || `¡${mascota.nombre} identificado exitosamente!`;
                        
                        // Verificar si la mascota está perdida y mostrar alerta
                        if (data.mascota_perdida) {
                            currentMascotaUuid = mascota.uuid;
                            currentMascotaNombre = mascota.nombre;
                            console.log('🔍 Mascota perdida detectada:', {
                                uuid: currentMascotaUuid,
                                nombre: currentMascotaNombre,
                                perdida: data.mascota_perdida
                            });
                            mostrarAlertaMascotaPerdida();
                        } else {
                            // Limpiar variables si no está perdida
                            currentMascotaUuid = null;
                            currentMascotaNombre = null;
                            ocultarAlertaMascotaPerdida();
                        }
                    } else {
                        // Mostrar resultado de error
                        resultError.classList.remove('hidden');
                        document.getElementById('result-error-message').textContent = reconocimiento.mensaje || 'No se pudo identificar la mascota con suficiente confianza.';
                    }
                } else {
                    // Mostrar error
                    resultLoading.classList.add('hidden');
                    resultError.classList.remove('hidden');
                    document.getElementById('result-error-message').textContent = data.error || 'Error en el proceso de reconocimiento.';
                }
            } catch (err) {
                console.error('Error en el reconocimiento:', err);
                
                // Mostrar error
                resultLoading.classList.add('hidden');
                resultError.classList.remove('hidden');
                document.getElementById('result-error-message').textContent = 'Error en el proceso de reconocimiento.';
            }
        }
    }
    
    // Función para comprimir y redimensionar imagen
    function compressImage(dataUrl, maxWidth = 1024, maxHeight = 1024, quality = 0.8) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Calcular nuevas dimensiones manteniendo proporción
                let { width, height } = img;
                
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width *= ratio;
                    height *= ratio;
                }
                
                // Configurar canvas
                canvas.width = width;
                canvas.height = height;
                
                // Dibujar imagen redimensionada
                ctx.drawImage(img, 0, 0, width, height);
                
                // Convertir a data URL comprimido
                const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
                resolve(compressedDataUrl);
            };
            img.src = dataUrl;
        });
    }
    
    // Función para convertir base64 a Blob
    function base64ToBlob(base64Data) {
        return new Promise((resolve) => {
            // Separar los datos del encabezado
            const [header, base64] = base64Data.split(';base64,');
            const contentType = header.split(':')[1];
            
            console.log('Content Type:', contentType); // Para depuración
            
            // Decodificar base64
            const byteCharacters = atob(base64);
            const byteArrays = [];
            
            for (let offset = 0; offset < byteCharacters.length; offset += 512) {
                const slice = byteCharacters.slice(offset, offset + 512);
                
                const byteNumbers = new Array(slice.length);
                for (let i = 0; i < slice.length; i++) {
                    byteNumbers[i] = slice.charCodeAt(i);
                }
                
                const byteArray = new Uint8Array(byteNumbers);
                byteArrays.push(byteArray);
            }
            
            // Crear un Blob con el tipo MIME adecuado
            const blob = new Blob(byteArrays, { type: contentType });
            
            // Añadir nombre de archivo para simular un archivo real
            blob.name = 'scanned_image.jpg';
            blob.lastModified = new Date();
            
            resolve(blob);
        });
    }
    
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
    

    
    // Variables globales para mascota actual
    let currentMascotaUuid = null;
    let currentMascotaNombre = null;
    let lastCapturedImage = null; // Guardar última imagen capturada para reportes
    
    /**
     * Verifica el estado de perdida de una mascota y muestra la alerta si es necesario
     */
    async function verificarYMostrarEstadoPerdida(mascotaUuid, mascotaNombre) {
        try {
            currentMascotaUuid = mascotaUuid;
            currentMascotaNombre = mascotaNombre;
            
            const response = await fetch(`/perdida/${mascotaUuid}/verificar-estado/`);
            const data = await response.json();
            
            if (data.success && data.mascota_perdida) {
                // Mostrar alerta de mascota perdida
                mostrarAlertaMascotaPerdida();
            } else {
                // Ocultar alerta si no está perdida
                ocultarAlertaMascotaPerdida();
            }
        } catch (error) {
            console.error('Error verificando estado de perdida:', error);
            ocultarAlertaMascotaPerdida();
        }
    }
    
    /**
     * Muestra la alerta de mascota perdida
     */
    function mostrarAlertaMascotaPerdida() {
        const alert = document.getElementById('mascota-perdida-alert');
        if (alert) {
            alert.classList.remove('hidden');
            
            // Configurar el botón de reportar encontrada
            const btnReportar = document.getElementById('btn-reportar-encontrada');
            if (btnReportar) {
                // Guardar datos en el botón
                btnReportar.setAttribute('data-mascota-uuid', currentMascotaUuid);
                btnReportar.setAttribute('data-mascota-nombre', currentMascotaNombre);
                btnReportar.onclick = () => reportarMascotaEncontradaEnScanner();
                console.log('✅ Botón configurado con datos:', {
                    uuid: currentMascotaUuid,
                    nombre: currentMascotaNombre
                });
            }
        }
    }
    
    /**
     * Oculta la alerta de mascota perdida
     */
    function ocultarAlertaMascotaPerdida() {
        const alert = document.getElementById('mascota-perdida-alert');
        if (alert) {
            alert.classList.add('hidden');
        }
    }
    
    /**
     * Reporta una mascota como encontrada desde el scanner
     */
    async function reportarMascotaEncontradaEnScanner() {
        // Intentar obtener datos del botón como backup
        const btnReportar = document.getElementById('btn-reportar-encontrada');
        let mascotaUuid = currentMascotaUuid;
        let mascotaNombre = currentMascotaNombre;
        
        if ((!mascotaUuid || !mascotaNombre) && btnReportar) {
            mascotaUuid = btnReportar.getAttribute('data-mascota-uuid');
            mascotaNombre = btnReportar.getAttribute('data-mascota-nombre');
            console.log('� Recuperando datos del botón:', { mascotaUuid, mascotaNombre });
        }
        
        console.log('�🐕 Intentando reportar mascota encontrada:', {
            uuid: mascotaUuid,
            nombre: mascotaNombre,
            source: (!currentMascotaUuid || !currentMascotaNombre) ? 'button-backup' : 'variables'
        });
        
        if (!mascotaUuid || !mascotaNombre) {
            console.error('❌ No hay mascota seleccionada para reportar');
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se ha detectado información de la mascota. Por favor, escanea nuevamente.'
            });
            return;
        }
        
        // Actualizar variables globales por si acaso
        currentMascotaUuid = mascotaUuid;
        currentMascotaNombre = mascotaNombre;
        
        const result = await Swal.fire({
            title: `¿Has encontrado a ${mascotaNombre}?`,
            html: `
                <div class="text-left">
                    <p class="text-gray-700 mb-3">
                        Si has encontrado a ${mascotaNombre}, confirma para notificar inmediatamente al propietario.
                    </p>
                    <p class="text-sm text-gray-600">
                        Se enviará automáticamente la ubicación aproximada y la hora del reporte.
                    </p>
                </div>
            `,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, la he encontrado',
            cancelButtonText: 'No, cancelar',
            confirmButtonColor: '#059669',
            cancelButtonColor: '#6b7280'
        });

        if (result.isConfirmed) {
            // Mostrar loading inicial
            Swal.fire({
                title: 'Obteniendo ubicación...',
                html: 'Solicitando permisos de ubicación para mejorar el reporte...',
                allowOutsideClick: false,
                showConfirmButton: false,
                willOpen: () => {
                    Swal.showLoading();
                }
            });

            // Obtener ubicación del usuario
            let ubicacionData = null;
            
            try {
                // Intentar obtener ubicación
                console.log('📍 Iniciando obtención de ubicación...');
                ubicacionData = await obtenerUbicacionUsuario();
                console.log('📍 Ubicación obtenida exitosamente:', ubicacionData);
            } catch (error) {
                console.error('❌ Error obteniendo ubicación:', error);
                console.error('❌ Error message:', error.message);
                console.error('❌ Error stack:', error.stack);
                
                // Mostrar advertencia al usuario
                await Swal.fire({
                    icon: 'warning',
                    title: 'Sin ubicación GPS',
                    html: `
                        <p>No se pudo obtener tu ubicación GPS.</p>
                        <p class="text-sm text-gray-600 mt-2">Motivo: ${error.message}</p>
                        <p class="text-sm text-gray-600 mt-2">El reporte se enviará sin información de ubicación.</p>
                    `,
                    confirmButtonText: 'Continuar de todas formas',
                    confirmButtonColor: '#10b981'
                });
            }

            // Actualizar loading
            Swal.fire({
                title: 'Reportando mascota encontrada...',
                html: 'Notificando al propietario...',
                allowOutsideClick: false,
                showConfirmButton: false,
                willOpen: () => {
                    Swal.showLoading();
                }
            });

            try {
                // Preparar datos de ubicación y foto
                const formData = new FormData();
                
                if (ubicacionData) {
                    if (ubicacionData.latitud && ubicacionData.longitud) {
                        formData.append('latitud', ubicacionData.latitud);
                        formData.append('longitud', ubicacionData.longitud);
                        console.log('📍 Enviando coordenadas:', {
                            lat: ubicacionData.latitud,
                            lng: ubicacionData.longitud
                        });
                    }
                    if (ubicacionData.direccion) {
                        formData.append('ubicacion_encontrada', ubicacionData.direccion);
                        console.log('📍 Enviando dirección:', ubicacionData.direccion);
                    }
                }
                
                // Agregar foto del reporte si existe
                if (lastCapturedImage) {
                    try {
                        // Convertir base64 a Blob
                        const blob = await base64ToBlob(lastCapturedImage);
                        formData.append('foto_reporte', blob, 'reporte_mascota.jpg');
                        console.log('📸 Foto del reporte agregada al formulario');
                    } catch (error) {
                        console.warn('⚠️ No se pudo agregar la foto al reporte:', error);
                        // Continuar sin foto
                    }
                }
                
                const response = await fetch(`/perdida/${mascotaUuid}/reportar-encontrada/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    await Swal.fire({
                        title: '¡Reporte exitoso!',
                        html: `
                            <div class="text-center">
                                <p class="text-lg text-gray-700 mb-3">${data.message}</p>
                                <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                                    <p class="text-sm text-green-800">
                                        <i class="fas fa-check-circle text-green-600 mr-1"></i>
                                        El propietario ${data.propietario_nombre} ha sido notificado por email.
                                    </p>
                                </div>
                            </div>
                        `,
                        icon: 'success',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#10b981'
                    });
                    
                    // Ocultar la alerta de perdida ya que fue reportada como encontrada
                    ocultarAlertaMascotaPerdida();
                    
                } else {
                    await Swal.fire({
                        title: 'Error',
                        text: data.error || 'No se pudo reportar la mascota como encontrada',
                        icon: 'error',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#dc2626'
                    });
                }
            } catch (error) {
                console.error('Error reportando mascota encontrada:', error);
                await Swal.fire({
                    title: 'Error de conexión',
                    text: 'No se pudo conectar con el servidor. Verifica tu conexión a internet.',
                    icon: 'error',
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc2626'
                });
            }
        }
    }

    /**
     * Obtiene la ubicación actual del usuario
     * @returns {Promise<Object>} Datos de ubicación
     */
    async function obtenerUbicacionUsuario() {
        console.log('🔍 obtenerUbicacionUsuario - Iniciando...');
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                console.error('❌ Geolocalización NO soportada');
                reject(new Error('Geolocalización no soportada por el navegador'));
                return;
            }

            console.log('✅ Geolocalización soportada');
            const options = {
                enableHighAccuracy: true, // Forzar uso de GPS para mayor precisión
                timeout: 20000, // 20 segundos para dar tiempo al GPS
                maximumAge: 0 // NO usar ubicación cacheada, siempre obtener nueva ubicación
            };
            console.log('📍 Opciones de geolocalización (alta precisión):', options);

            console.log('📍 Llamando a navigator.geolocation.getCurrentPosition...');
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log('✅ getCurrentPosition - Success callback');
                    console.log('📍 Position object:', position);
                    console.log('📍 Coords:', position.coords);
                    
                    const ubicacion = {
                        latitud: position.coords.latitude,
                        longitud: position.coords.longitude,
                        precision: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    
                    console.log('✅ Ubicación construida:', ubicacion);

                    // Intentar obtener dirección legible
                    console.log('🔍 Intentando geocodificación inversa...');
                    obtenerDireccionPorCoordenadas(ubicacion.latitud, ubicacion.longitud)
                        .then(direccion => {
                            console.log('✅ Dirección obtenida:', direccion);
                            ubicacion.direccion = direccion;
                            console.log('✅ Resolviendo con ubicacion completa:', ubicacion);
                            resolve(ubicacion);
                        })
                        .catch((geocodeError) => {
                            console.warn('⚠️ Geocodificación falló:', geocodeError);
                            // Si falla la geocodificación inversa, devolver solo coordenadas
                            console.log('✅ Resolviendo con solo coordenadas:', ubicacion);
                            resolve(ubicacion);
                        });
                },
                (error) => {
                    console.error('❌ getCurrentPosition - Error callback');
                    console.error('❌ Error code:', error.code);
                    console.error('❌ Error message:', error.message);
                    console.error('❌ Error object:', error);
                    
                    let mensaje = 'Error desconocido';
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            mensaje = 'Permisos de ubicación denegados. Por favor, permite el acceso a tu ubicación en la configuración del navegador.';
                            console.error('❌ Usuario denegó permisos');
                            break;
                        case error.POSITION_UNAVAILABLE:
                            mensaje = 'Ubicación no disponible. Asegúrate de que el GPS esté activado.';
                            console.error('❌ Posición no disponible');
                            break;
                        case error.TIMEOUT:
                            mensaje = 'Tiempo de espera agotado. Intenta de nuevo.';
                            console.error('❌ Timeout obteniendo ubicación');
                            break;
                    }
                    
                    console.error('❌ Rechazando promise con:', mensaje);
                    reject(new Error(mensaje));
                },
                options
            );
        });
    }

    /**
     * Obtiene dirección legible a partir de coordenadas usando OpenStreetMap
     * @param {number} lat - Latitud
     * @param {number} lng - Longitud
     * @returns {Promise<string>} Dirección legible
     */
    async function obtenerDireccionPorCoordenadas(lat, lng) {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
            const data = await response.json();
            
            if (data && data.display_name) {
                return data.display_name;
            } else {
                return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
            }
        } catch (error) {
            console.error('Error en geocodificación inversa:', error);
            return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        }
    }

    // ============================================
    // SCANNER CONTINUO - Reconocimiento en tiempo real
    // ============================================
    
    let continuousScannerStream = null;
    let continuousScannerInterval = null;
    let continuousScannerActive = false;
    let continuousAnalysisCount = 0;
    let isAnalyzing = false;
    
    /**
     * Inicializa el scanner continuo
     */
    function initContinuousScanner() {
        const video = document.getElementById('scanner-continuous-video');
        const toggleBtn = document.getElementById('scanner-continuous-toggle');
        const intervalSlider = document.getElementById('scanner-continuous-interval');
        const intervalValue = document.getElementById('scanner-interval-value');
        const tabButtons = document.querySelectorAll('.scan-tab-btn');
        
        if (!video || !toggleBtn) {
            console.warn('Elementos del scanner continuo no encontrados');
            return;
        }
        
        // Actualizar valor del intervalo cuando se mueve el slider
        if (intervalSlider && intervalValue) {
            intervalSlider.addEventListener('input', (e) => {
                intervalValue.textContent = e.target.value;
            });
        }
        
        // Evento del botón de toggle
        toggleBtn.addEventListener('click', async () => {
            if (!continuousScannerActive) {
                await startContinuousScanning();
            } else {
                stopContinuousScanning();
            }
        });
        
        // Detectar cambio de pestaña para detener el scanner
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const target = button.dataset.target;
                if (target !== 'continuous-tab' && continuousScannerActive) {
                    stopContinuousScanning();
                }
            });
        });
        
        // NO inicializar la cámara automáticamente cuando se activa la pestaña
        // El usuario debe presionar "Iniciar escaneo" para comenzar
        
        // Configurar el botón de reiniciar
        const resetBtn = document.getElementById('scanner-continuous-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                resetContinuousScanner();
            });
        }
        
        // Configurar selector de cámaras
        const cameraSelect = document.getElementById('scanner-continuous-camera-select');
        const switchCameraBtn = document.getElementById('scanner-continuous-switch-camera');
        
        if (cameraSelect && switchCameraBtn) {
            switchCameraBtn.addEventListener('click', async () => {
                const selectedDeviceId = cameraSelect.value;
                if (selectedDeviceId) {
                    await switchContinuousCamera(selectedDeviceId);
                }
            });
            
            cameraSelect.addEventListener('change', async () => {
                const selectedDeviceId = cameraSelect.value;
                if (selectedDeviceId && continuousScannerStream) {
                    await switchContinuousCamera(selectedDeviceId);
                }
            });
        }
    }
    
    /**
     * Inicializa la cámara para el scanner continuo
     */
    async function initContinuousCamera(deviceId = null) {
        const video = document.getElementById('scanner-continuous-video');
        const toggleBtn = document.getElementById('scanner-continuous-toggle');
        const cameraSelectContainer = document.getElementById('scanner-continuous-camera-select-container');
        const cameraSelect = document.getElementById('scanner-continuous-camera-select');
        const switchCameraBtn = document.getElementById('scanner-continuous-switch-camera');
        
        if (!video) {
            return;
        }
        
        try {
            // Configuración del video - compatible con laptop y móvil
            let constraints;
            if (deviceId) {
                // Si se especifica un dispositivo, usarlo
                constraints = { 
                    video: { 
                        deviceId: { exact: deviceId },
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                };
            } else {
                // Intentar primero con facingMode para móviles
                constraints = { 
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                };
            }
            
            let stream;
            try {
                stream = await navigator.mediaDevices.getUserMedia(constraints);
            } catch (error) {
                // Si falla (probablemente en laptop), intentar sin facingMode
                console.log('Intento con facingMode falló, intentando sin restricciones específicas...');
                constraints = { 
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                };
                stream = await navigator.mediaDevices.getUserMedia(constraints);
            }
            
            video.srcObject = stream;
            continuousScannerStream = stream;
            
            // Listar cámaras disponibles
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            
            if (videoDevices.length > 1 && cameraSelect && cameraSelectContainer) {
                // Limpiar opciones existentes
                cameraSelect.innerHTML = '';
                
                // Agregar opciones de cámaras
                videoDevices.forEach((device, index) => {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.text = device.label || `Cámara ${index + 1}`;
                    cameraSelect.appendChild(option);
                });
                
                // Seleccionar la cámara actual
                const currentTrack = stream.getVideoTracks()[0];
                const currentDeviceId = currentTrack.getSettings().deviceId;
                cameraSelect.value = currentDeviceId;
                
                // Mostrar selector de cámaras
                cameraSelectContainer.style.display = 'block';
                if (switchCameraBtn) {
                    switchCameraBtn.disabled = false;
                }
            }
            
            // El botón ya está habilitado por defecto, no necesitamos hacer nada más
            
        } catch (error) {
            console.error('Error al inicializar cámara continua:', error);
            showMessage('No se pudo acceder a la cámara. Verifica los permisos.', 'error');
            throw error; // Re-lanzar el error para manejarlo en startContinuousScanning
        }
    }
    
    /**
     * Cambia la cámara del scanner continuo
     */
    async function switchContinuousCamera(deviceId) {
        const video = document.getElementById('scanner-continuous-video');
        
        // Detener stream actual
        if (continuousScannerStream) {
            const tracks = continuousScannerStream.getTracks();
            tracks.forEach(track => track.stop());
            continuousScannerStream = null;
        }
        
        // Inicializar con nueva cámara
        await initContinuousCamera(deviceId);
    }
    
    /**
     * Inicia el escaneo continuo
     */
    async function startContinuousScanning() {
        const video = document.getElementById('scanner-continuous-video');
        const toggleBtn = document.getElementById('scanner-continuous-toggle');
        const toggleText = document.getElementById('scanner-continuous-toggle-text');
        const intervalSlider = document.getElementById('scanner-continuous-interval');
        const resultDiv = document.getElementById('scanner-continuous-result');
        
        // Inicializar cámara si no está activa
        if (!video || !video.srcObject) {
            toggleBtn.disabled = true;
            toggleBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Iniciando cámara...';
            
            try {
                await initContinuousCamera();
                
                if (!video || !video.srcObject) {
                    throw new Error('No se pudo obtener stream de video');
                }
                
                // Esperar a que el video esté completamente cargado
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => reject(new Error('Timeout al cargar video')), 10000);
                    
                    if (video.readyState >= 2) {
                        clearTimeout(timeout);
                        resolve();
                    } else {
                        video.onloadedmetadata = () => {
                            clearTimeout(timeout);
                            resolve();
                        };
                    }
                });
            } catch (error) {
                console.error('Error al iniciar cámara:', error);
                showMessage('No se pudo iniciar la cámara. Verifica los permisos.', 'error');
                
                // Restaurar botón a estado inicial
                toggleBtn.disabled = false;
                toggleBtn.innerHTML = '<i class="fas fa-play mr-2"></i> <span id="scanner-continuous-toggle-text">Iniciar escaneo</span>';
                return;
            }
        }
        
        continuousScannerActive = true;
        continuousAnalysisCount = 0;
        updateAnalysisCount();
        
        // Actualizar botón
        if (toggleBtn) {
            toggleBtn.disabled = false; // Asegurar que esté habilitado
            toggleBtn.classList.remove('bg-primary-600', 'hover:bg-primary-700');
            toggleBtn.classList.add('bg-red-600', 'hover:bg-red-700');
            toggleBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> <span id="scanner-continuous-toggle-text">Detener escaneo</span>';
        }
        
        // Deshabilitar slider durante el escaneo
        if (intervalSlider) {
            intervalSlider.disabled = true;
        }
        
        // Mostrar resultado overlay con mensaje inicial
        if (resultDiv) {
            resultDiv.classList.remove('hidden');
            const petNameEl = document.getElementById('scanner-continuous-pet-name');
            const petInfoEl = document.getElementById('scanner-continuous-pet-info');
            const statusIconEl = document.getElementById('scanner-continuous-status-icon');
            
            if (petNameEl && petInfoEl && statusIconEl) {
                petNameEl.textContent = '🔍 Iniciando escaneo...';
                petInfoEl.innerHTML = '<p class="text-blue-600"><i class="fas fa-radar mr-1"></i> Buscando mascotas...</p>';
                statusIconEl.innerHTML = '<i class="fas fa-circle-notch fa-spin text-blue-500"></i>';
            }
        }
        
        // Iniciar captura periódica
        const interval = parseFloat(intervalSlider?.value || 3) * 1000;
        continuousScannerInterval = setInterval(() => {
            if (continuousScannerActive && !isAnalyzing) {
                captureAndRecognizeFrame();
            }
        }, interval);
        
        // Hacer primera captura inmediatamente
        captureAndRecognizeFrame();
    }
    
    /**
     * Detiene el escaneo continuo
     */
    function stopContinuousScanning() {
        const toggleBtn = document.getElementById('scanner-continuous-toggle');
        const intervalSlider = document.getElementById('scanner-continuous-interval');
        const analyzingIndicator = document.getElementById('scanner-analyzing-indicator');
        const recognitionResult = document.getElementById('recognition-result');
        
        continuousScannerActive = false;
        
        if (continuousScannerInterval) {
            clearInterval(continuousScannerInterval);
            continuousScannerInterval = null;
        }
        
        // Actualizar botón
        if (toggleBtn) {
            toggleBtn.disabled = false; // Asegurar que esté habilitado
            toggleBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
            toggleBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
            toggleBtn.innerHTML = '<i class="fas fa-play mr-2"></i> <span id="scanner-continuous-toggle-text">Iniciar escaneo</span>';
        }
        
        // Habilitar slider
        if (intervalSlider) {
            intervalSlider.disabled = false;
        }
        
        // Ocultar indicador de análisis
        if (analyzingIndicator) {
            analyzingIndicator.style.display = 'none';
        }
        
        // Resetear atributo de scroll para permitir scroll en próximo inicio
        if (recognitionResult) {
            recognitionResult.removeAttribute('data-scrolled');
        }
        
        // Resetear estado de análisis
        isAnalyzing = false;
        
        // Resetear resultado
        resetContinuousResult();
    }
    
    /**
     * Captura un frame del video y lo envía para reconocimiento
     */
    async function captureAndRecognizeFrame() {
        if (isAnalyzing || !continuousScannerActive) {
            return;
        }
        
        const video = document.getElementById('scanner-continuous-video');
        const canvas = document.getElementById('scanner-canvas');
        const analyzingIndicator = document.getElementById('scanner-analyzing-indicator');
        
        if (!video || !canvas) {
            return;
        }
        
        isAnalyzing = true;
        
        // Mostrar indicador de análisis
        if (analyzingIndicator) {
            analyzingIndicator.style.display = 'flex';
        }
        
        try {
            // Capturar frame
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            
            // Convertir a base64
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Enviar al endpoint existente
            const formData = new FormData();
            formData.append('imagen', dataURItoBlob(imageData), 'frame.jpg');
            
            const response = await fetch('/scanner/upload-recognition/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            
            // Incrementar contador
            continuousAnalysisCount++;
            updateAnalysisCount();
            
            // Mostrar resultado
            if (data.success) {
                displayContinuousResult(data);
            } else {
                displayContinuousNoMatch();
            }
            
        } catch (error) {
            console.error('Error en captura y reconocimiento:', error);
            displayContinuousError();
        } finally {
            isAnalyzing = false;
            // Ocultar indicador de análisis
            if (analyzingIndicator) {
                analyzingIndicator.style.display = 'none';
            }
        }
    }
    
    /**
     * Muestra el resultado del reconocimiento en tiempo real
     */
    function displayContinuousResult(data) {
        // Ocultar el overlay del video temporalmente
        const overlayResult = document.getElementById('scanner-continuous-result');
        if (overlayResult) {
            overlayResult.classList.add('hidden');
        }
        
        // Obtener referencias a los elementos de UI
        const recognitionResult = document.getElementById('recognition-result');
        const resultLoading = document.getElementById('result-loading');
        const resultSuccess = document.getElementById('result-success');
        const resultError = document.getElementById('result-error');
        
        // Mostrar sección de resultados (sin loading, directo)
        if (recognitionResult) recognitionResult.classList.remove('hidden');
        if (resultLoading) resultLoading.classList.add('hidden');
        if (resultError) resultError.classList.add('hidden');
        
        if (data.success) {
            const reconocimiento = data.reconocimiento;
            
            if (reconocimiento && reconocimiento.exito) {
                // Mostrar resultado exitoso
                if (resultSuccess) resultSuccess.classList.remove('hidden');
                
                const mascota = data.mascota;
                const propietario = data.propietario;
                
                // Actualizar información principal de la mascota
                const nombreEl = document.getElementById('result-nombre');
                if (nombreEl) nombreEl.textContent = mascota.nombre || 'Sin nombre';
                
                // Solo raza (sin especie)
                const razaTexto = mascota.raza || 'Sin raza específica';
                const razaEl = document.getElementById('result-raza');
                if (razaEl) {
                    const spanEl = razaEl.querySelector('span');
                    if (spanEl) spanEl.textContent = razaTexto;
                }
                
                // Edad y peso
                const edadTexto = mascota.edad ? `${mascota.edad} años` : 'Edad desconocida';
                const pesoTexto = mascota.peso ? `${mascota.peso} kg` : 'Peso no registrado';
                const edadPesoEl = document.getElementById('result-edad-peso');
                if (edadPesoEl) {
                    const spanEl = edadPesoEl.querySelector('span');
                    if (spanEl) spanEl.textContent = `${edadTexto} • ${pesoTexto}`;
                }
                
                // Foto de la mascota
                const fotoMascota = document.getElementById('result-foto-mascota');
                const iconoMascota = document.getElementById('result-icono-mascota');
                if (fotoMascota && iconoMascota) {
                    if (mascota.foto_perfil) {
                        fotoMascota.src = mascota.foto_perfil;
                        fotoMascota.classList.remove('hidden');
                        iconoMascota.classList.add('hidden');
                    } else {
                        fotoMascota.classList.add('hidden');
                        iconoMascota.classList.remove('hidden');
                    }
                }
                
                // Información del propietario
                if (propietario) {
                    const propNombreEl = document.getElementById('result-propietario-nombre');
                    if (propNombreEl) propNombreEl.textContent = propietario.nombre_completo || 'Sin nombre';
                    
                    const propEmailEl = document.getElementById('result-propietario-email');
                    if (propEmailEl) {
                        const spanEl = propEmailEl.querySelector('span');
                        if (spanEl) spanEl.textContent = propietario.email || 'Sin email';
                    }
                    
                    const propTelEl = document.getElementById('result-propietario-telefono');
                    if (propTelEl) {
                        const spanEl = propTelEl.querySelector('span');
                        if (spanEl) spanEl.textContent = propietario.telefono || 'Sin teléfono';
                    }
                    
                    // Foto del propietario
                    const fotoPropietario = document.getElementById('result-foto-propietario');
                    const iconoPropietario = document.getElementById('result-icono-propietario');
                    if (fotoPropietario && iconoPropietario) {
                        if (propietario.foto_perfil) {
                            fotoPropietario.src = propietario.foto_perfil;
                            fotoPropietario.classList.remove('hidden');
                            iconoPropietario.classList.add('hidden');
                        } else {
                            fotoPropietario.classList.add('hidden');
                            iconoPropietario.classList.remove('hidden');
                        }
                    }
                }
                
                // Detalles adicionales
                const colorEl = document.getElementById('result-color');
                if (colorEl) colorEl.textContent = mascota.color || '-';
                
                const generoEl = document.getElementById('result-genero');
                if (generoEl) generoEl.textContent = mascota.genero || '-';
                
                const etapaEl = document.getElementById('result-etapa-vida');
                if (etapaEl) etapaEl.textContent = mascota.etapa_vida || '-';
                
                const estadoEl = document.getElementById('result-estado-salud');
                if (estadoEl) estadoEl.textContent = mascota.estado_salud || 'Normal';
                
                // Confianza y tiempo
                const confianzaEl = document.getElementById('result-confianza');
                if (confianzaEl && reconocimiento.confianza !== undefined) {
                    confianzaEl.textContent = `Confianza: ${(reconocimiento.confianza * 100).toFixed(1)}%`;
                    
                    // Actualizar clases de confianza
                    confianzaEl.className = 'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium';
                    
                    if (reconocimiento.confianza >= 0.9) {
                        confianzaEl.classList.add('bg-green-100', 'text-green-800');
                    } else if (reconocimiento.confianza >= 0.7) {
                        confianzaEl.classList.add('bg-blue-100', 'text-blue-800');
                    } else {
                        confianzaEl.classList.add('bg-yellow-100', 'text-yellow-800');
                    }
                }
                
                const tiempoEl = document.getElementById('result-tiempo');
                if (tiempoEl && reconocimiento.tiempo_procesamiento !== undefined) {
                    tiempoEl.textContent = `${reconocimiento.tiempo_procesamiento.toFixed(2)}s`;
                }
                
                // Mensaje de éxito personalizado
                const mensajeEl = document.getElementById('result-success-message');
                if (mensajeEl) {
                    mensajeEl.textContent = reconocimiento.mensaje || `¡${mascota.nombre} identificado exitosamente!`;
                }
                
                // Verificar si la mascota está perdida y mostrar alerta
                if (data.mascota_perdida) {
                    currentMascotaUuid = mascota.uuid;
                    currentMascotaNombre = mascota.nombre;
                    if (typeof mostrarAlertaMascotaPerdida === 'function') {
                        mostrarAlertaMascotaPerdida();
                    }
                } else {
                    currentMascotaUuid = null;
                    currentMascotaNombre = null;
                    if (typeof ocultarAlertaMascotaPerdida === 'function') {
                        ocultarAlertaMascotaPerdida();
                    }
                }
                
                // Hacer scroll suave hacia los resultados (solo la primera vez)
                setTimeout(() => {
                    if (recognitionResult && !recognitionResult.hasAttribute('data-scrolled')) {
                        recognitionResult.setAttribute('data-scrolled', 'true');
                        recognitionResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }, 100);
            } else {
                // No se pudo reconocer con suficiente confianza
                displayContinuousNoMatch();
            }
        } else {
            // Error en la respuesta
            displayContinuousNoMatch();
        }
    }
    
    /**
     * Muestra mensaje cuando no hay coincidencia
     */
    function displayContinuousNoMatch() {
        // Mostrar en el overlay (mensaje temporal)
        const petNameEl = document.getElementById('scanner-continuous-pet-name');
        const petInfoEl = document.getElementById('scanner-continuous-pet-info');
        const statusIconEl = document.getElementById('scanner-continuous-status-icon');
        const resultDiv = document.getElementById('scanner-continuous-result');
        
        if (petNameEl && petInfoEl && statusIconEl) {
            petNameEl.textContent = 'No se pudo reconocer';
            petInfoEl.innerHTML = '<p class="text-gray-600"><i class="fas fa-search mr-1"></i> Seguiremos intentando detectar una mascota...</p>';
            statusIconEl.innerHTML = '<i class="fas fa-search text-blue-500"></i>';
            
            // Mostrar el overlay brevemente
            if (resultDiv) {
                resultDiv.classList.remove('hidden');
            }
        }
        
        // NO ocultar el panel de resultados si ya hay una mascota detectada previamente
        // Esto mantiene la información de la última mascota reconocida
    }
    
    /**
     * Muestra mensaje de error
     */
    function displayContinuousError() {
        // Mostrar en el overlay (mensaje temporal)
        const petNameEl = document.getElementById('scanner-continuous-pet-name');
        const petInfoEl = document.getElementById('scanner-continuous-pet-info');
        const statusIconEl = document.getElementById('scanner-continuous-status-icon');
        const resultDiv = document.getElementById('scanner-continuous-result');
        
        if (petNameEl && petInfoEl && statusIconEl) {
            petNameEl.textContent = 'No se pudo reconocer';
            petInfoEl.innerHTML = '<p class="text-orange-600"><i class="fas fa-exclamation-circle mr-1"></i> Continuaremos intentando...</p>';
            statusIconEl.innerHTML = '<i class="fas fa-redo text-orange-500"></i>';
            
            // Mostrar el overlay brevemente
            if (resultDiv) {
                resultDiv.classList.remove('hidden');
            }
        }
        
        // NO ocultar el panel de resultados si ya hay una mascota detectada previamente
        // Esto mantiene la información de la última mascota reconocida
    }
    
    /**
     * Resetea el resultado continuo
     */
    function resetContinuousResult() {
        const petNameEl = document.getElementById('scanner-continuous-pet-name');
        const petInfoEl = document.getElementById('scanner-continuous-pet-info');
        const statusIconEl = document.getElementById('scanner-continuous-status-icon');
        const overlayResultDiv = document.getElementById('scanner-continuous-result');
        
        if (petNameEl && petInfoEl && statusIconEl) {
            petNameEl.textContent = 'Buscando mascota...';
            petInfoEl.innerHTML = '<p class="text-gray-500"><i class="fas fa-play-circle mr-1"></i> Presiona iniciar para comenzar</p>';
            statusIconEl.innerHTML = '<i class="fas fa-paw text-gray-400"></i>';
        }
        
        // Ocultar el overlay del video
        if (overlayResultDiv) {
            overlayResultDiv.classList.add('hidden');
        }
        
        // NO ocultar el panel principal de resultados
        // Esto permite que la información de la última mascota detectada permanezca visible
    }
    
    /**
     * Actualiza el contador de análisis
     */
    function updateAnalysisCount() {
        const countEl = document.getElementById('scanner-continuous-count');
        if (countEl) {
            countEl.textContent = continuousAnalysisCount;
        }
    }
    
    /**
     * Reinicia completamente el scanner continuo
     */
    function resetContinuousScanner() {
        // Detener el escaneo si está activo
        if (continuousScannerActive) {
            stopContinuousScanning();
        }
        
        // Detener la cámara
        const video = document.getElementById('scanner-continuous-video');
        if (continuousScannerStream) {
            const tracks = continuousScannerStream.getTracks();
            tracks.forEach(track => track.stop());
            continuousScannerStream = null;
        }
        
        if (video) {
            video.srcObject = null;
        }
        
        // Resetear contador
        continuousAnalysisCount = 0;
        updateAnalysisCount();
        
        // Resetear botón
        const toggleBtn = document.getElementById('scanner-continuous-toggle');
        if (toggleBtn) {
            toggleBtn.disabled = false;
            toggleBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
            toggleBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
            toggleBtn.innerHTML = '<i class="fas fa-play mr-2"></i> <span id="scanner-continuous-toggle-text">Iniciar escaneo</span>';
        }
        
        // Resetear slider
        const intervalSlider = document.getElementById('scanner-continuous-interval');
        if (intervalSlider) {
            intervalSlider.value = 3;
            intervalSlider.disabled = false;
        }
        
        const intervalValue = document.getElementById('scanner-interval-value');
        if (intervalValue) {
            intervalValue.textContent = '3';
        }
        
        // Ocultar selector de cámaras
        const cameraSelectContainer = document.getElementById('scanner-continuous-camera-select-container');
        if (cameraSelectContainer) {
            cameraSelectContainer.style.display = 'none';
        }
        
        // Ocultar overlay de resultados
        const overlayResult = document.getElementById('scanner-continuous-result');
        if (overlayResult) {
            overlayResult.classList.add('hidden');
        }
        
        // Ocultar panel de resultados
        const recognitionResult = document.getElementById('recognition-result');
        if (recognitionResult) {
            recognitionResult.classList.add('hidden');
            recognitionResult.removeAttribute('data-scrolled');
        }
        
        // Ocultar indicador de análisis
        const analyzingIndicator = document.getElementById('scanner-analyzing-indicator');
        if (analyzingIndicator) {
            analyzingIndicator.style.display = 'none';
        }
        
        // Resetear estados
        continuousScannerActive = false;
        isAnalyzing = false;
        
        showMessage('Scanner continuo reiniciado', 'success');
    }
    
    /**
     * Convierte data URI a Blob
     */
    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(',')[1]);
        const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], { type: mimeString });
    }
    
    /**
     * Obtiene cookie por nombre (para CSRF token)
     */
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
    
    // Inicializar el scanner continuo cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', () => {
        initContinuousScanner();
    });
