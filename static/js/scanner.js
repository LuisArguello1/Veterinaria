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
                    stopScannerCamera();
                }
            });
        });
    }
    
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
                
                // Cambiar comportamiento a detener cámara
                startCameraBtn.onclick = () => stopScannerCamera();
                
                cameraOverlay.classList.add('hidden');
                
                return true;
            } catch (err) {
                console.error('Error al acceder a la cámara:', err);
                alert('No se pudo acceder a la cámara. Por favor, verifica que has concedido permisos.');
                cameraOverlay.classList.add('hidden');
                return false;
            }
        }
        
        // Inicializar cámara
        if (startCameraBtn && !disabled) {
            startCameraBtn.addEventListener('click', async () => {
                await startCamera();
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
                
                // Configurar canvas con dimensiones del video
                canvas.width = webcamVideo.videoWidth;
                canvas.height = webcamVideo.videoHeight;
                
                // Dibujar frame actual del video en el canvas
                const context = canvas.getContext('2d');
                context.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
                
                // Obtener imagen como base64 comprimida (calidad 0.8 para reducir tamaño)
                const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
                
                // Detener cámara
                stopScannerCamera();
                
                // Mostrar resultados y procesar reconocimiento
                processRecognition(imageDataUrl);
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
        
        // Función para detener la cámara
        function stopScannerCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                webcamVideo.srcObject = null;
                stream = null;
                
                // Restaurar botón de iniciar cámara
                startCameraBtn.innerHTML = '<i class="fas fa-play mr-2"></i> Iniciar cámara';
                startCameraBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
                startCameraBtn.classList.add('bg-primary-600', 'hover:bg-primary-700');
                
                // Restaurar comportamiento
                startCameraBtn.onclick = null;
                
                // Deshabilitar botón de captura
                capturePhotoBtn.disabled = true;
                
                // Ocultar selector de cámaras
                cameraSelectContainer.style.display = 'none';
            }
        }
        
        // Función para manejar archivo seleccionado
        function handleFileSelect(files) {
            if (files && files.length > 0) {
                const file = files[0];
                
                if (!file.type.startsWith('image/')) {
                    alert('Por favor, selecciona una imagen.');
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
                // Mostrar sección de resultados
                recognitionResult.classList.remove('hidden');
                resultLoading.classList.remove('hidden');
                resultSuccess.classList.add('hidden');
                resultError.classList.add('hidden');
                
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
                ubicacionData = await obtenerUbicacionUsuario();
                console.log('📍 Ubicación obtenida:', ubicacionData);
            } catch (error) {
                console.log('📍 No se pudo obtener ubicación:', error);
                // Continuar sin ubicación
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
                const response = await fetch(`/perdida/${mascotaUuid}/reportar-encontrada/`, {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        ubicacion: ubicacionData
                    })
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
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocalización no soportada por el navegador'));
                return;
            }

            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutos
            };

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const ubicacion = {
                        latitud: position.coords.latitude,
                        longitud: position.coords.longitude,
                        precision: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };

                    // Intentar obtener dirección legible
                    obtenerDireccionPorCoordenadas(ubicacion.latitud, ubicacion.longitud)
                        .then(direccion => {
                            ubicacion.direccion = direccion;
                            resolve(ubicacion);
                        })
                        .catch(() => {
                            // Si falla la geocodificación inversa, devolver solo coordenadas
                            resolve(ubicacion);
                        });
                },
                (error) => {
                    console.error('Error obteniendo ubicación:', error);
                    let mensaje = 'Error desconocido';
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            mensaje = 'Permisos de ubicación denegados';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            mensaje = 'Ubicación no disponible';
                            break;
                        case error.TIMEOUT:
                            mensaje = 'Tiempo de espera agotado';
                            break;
                    }
                    
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