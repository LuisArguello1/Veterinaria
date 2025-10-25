/**
 * Sistema de Reconocimiento Facial
 * Maneja la captura de video, detección de rostros y registro de biometría
 */

class FacialRecognitionManager {
    constructor(config) {
        console.log('FacialRecognitionManager constructor called with config:', config);
        
        this.config = config;
        
        // Elementos del DOM
        this.video = document.getElementById('webcam');
        this.overlay = document.getElementById('overlay');
        this.statusText = document.getElementById('statusText');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.captureBtn = document.getElementById('captureBtn');
        this.deleteBtn = document.getElementById('deleteBtn');
        this.toggleBtn = document.getElementById('toggleBtn');
        
        console.log('DOM Elements:', {
            video: this.video,
            overlay: this.overlay,
            statusText: this.statusText,
            captureBtn: this.captureBtn
        });
        
        if (!this.video || !this.overlay) {
            throw new Error('No se encontraron los elementos de video necesarios en la página');
        }
        
        // Estado
        this.stream = null;
        this.isDetecting = false;
        this.faceDetected = false;
        this.detectionInterval = null;
        
        // Configuración
        this.detectionIntervalMs = 500; // Detectar cada 500ms
        
        this.init();
    }
    
    init() {
        console.log('Initializing FacialRecognitionManager...');
        this.setupEventListeners();
        this.startCamera();
    }
    
    setupEventListeners() {
        console.log('Setting up event listeners...');
        // Botón de captura
        if (this.captureBtn) {
            this.captureBtn.addEventListener('click', () => this.captureFace());
        }
        
        // Botón de eliminar
        if (this.deleteBtn) {
            this.deleteBtn.addEventListener('click', () => this.deleteBiometry());
        }
        
        // Botón de toggle
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => this.toggleFacialLogin());
        }
    }
    
    async startCamera() {
        try {
            this.updateStatus('Iniciando cámara...', 'detecting');
            
            // Verificar si el navegador soporta getUserMedia
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Tu navegador no soporta acceso a la cámara. Usa Chrome, Firefox o Edge.');
            }
            
            console.log('Solicitando acceso a la cámara...');
            
            // Solicitar acceso a la cámara
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                }
            });
            
            console.log('Acceso a cámara concedido');
            
            this.video.srcObject = this.stream;
            
            // Esperar a que el video esté listo
            await new Promise((resolve, reject) => {
                this.video.onloadedmetadata = () => {
                    console.log('Video metadata cargada');
                    this.video.play().then(() => {
                        console.log('Video iniciado');
                        resolve();
                    }).catch(reject);
                };
                
                this.video.onerror = (error) => {
                    console.error('Error en elemento video:', error);
                    reject(new Error('Error al cargar el video'));
                };
                
                // Timeout de 10 segundos
                setTimeout(() => reject(new Error('Timeout al cargar la cámara')), 10000);
            });
            
            // Configurar canvas overlay
            this.overlay.width = this.video.videoWidth;
            this.overlay.height = this.video.videoHeight;
            
            console.log('Canvas configurado:', this.overlay.width, 'x', this.overlay.height);
            
            this.updateStatus('Cámara iniciada. Buscando rostro...', 'detecting');
            
            // Habilitar botón de captura
            if (this.captureBtn) {
                this.captureBtn.disabled = false;
            }
            
            // Iniciar detección automática
            this.startDetection();
            
        } catch (error) {
            console.error('Error al acceder a la cámara:', error);
            
            let errorMessage = 'Error al acceder a la cámara. ';
            
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage += 'Permiso denegado. Por favor, permite el acceso a la cámara en tu navegador.';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage += 'No se encontró ninguna cámara conectada.';
            } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                errorMessage += 'La cámara está siendo usada por otra aplicación.';
            } else {
                errorMessage += error.message || 'Error desconocido.';
            }
            
            this.updateStatus(errorMessage, 'error');
            this.showNotification('error', errorMessage);
        }
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.stopDetection();
    }
    
    startDetection() {
        this.stopDetection();
        
        this.detectionInterval = setInterval(() => {
            if (!this.isDetecting) {
                this.detectFace();
            }
        }, this.detectionIntervalMs);
    }
    
    stopDetection() {
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
    }
    
    async detectFace() {
        if (this.isDetecting || !this.video.videoWidth) return;
        
        this.isDetecting = true;
        
        try {
            // Capturar frame actual
            const imageData = this.captureFrame();
            
            // Enviar al servidor para detección
            const response = await fetch(this.config.urls.detect, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const data = await response.json();
            
            if (data.success && data.face_detected) {
                this.faceDetected = true;
                this.updateStatus(
                    `✓ Rostro detectado (Confianza: ${(data.confidence * 100).toFixed(1)}%)`,
                    'detected'
                );
                this.drawFaceBox(data.bbox, data.confidence);
            } else {
                this.faceDetected = false;
                this.updateStatus('Buscando rostro...', 'detecting');
                this.clearOverlay();
            }
            
        } catch (error) {
            console.error('Error en detección:', error);
        } finally {
            this.isDetecting = false;
        }
    }
    
    captureFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0);
        
        return canvas.toDataURL('image/jpeg', 0.9);
    }
    
    async captureFace() {
        if (!this.faceDetected) {
            this.showNotification('warning', 'Por favor, espera a que se detecte tu rostro');
            return;
        }
        
        // Deshabilitar botón temporalmente
        this.captureBtn.disabled = true;
        this.captureBtn.innerHTML = `
            <div class="loading-spinner"></div>
            <span>Procesando...</span>
        `;
        
        try {
            const imageData = this.captureFrame();
            
            this.updateStatus('Registrando biometría...', 'detecting');
            
            const response = await fetch(this.config.urls.register, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateStatus('✓ Biometría registrada exitosamente', 'detected');
                this.showNotification('success', data.message);
                
                // Recargar la página después de 2 segundos
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                this.updateStatus('Error al registrar biometría', 'error');
                this.showNotification('error', data.message);
            }
            
        } catch (error) {
            console.error('Error al capturar rostro:', error);
            this.updateStatus('Error al registrar', 'error');
            this.showNotification('error', 'Error al comunicarse con el servidor');
        } finally {
            // Restaurar botón
            this.captureBtn.disabled = false;
            this.captureBtn.innerHTML = `
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span>Capturar Rostro</span>
            `;
        }
    }
    
    async deleteBiometry() {
        try {
            const result = await Swal.fire({
                title: '¿Estás seguro?',
                text: 'Esta acción eliminará tu biometría facial registrada',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#ef4444',
                cancelButtonColor: '#6b7280',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });

            if (!result.isConfirmed) {
                return;
            }

            // Deshabilitar botón y mostrar loading
            if (this.deleteBtn) {
                this.deleteBtn.disabled = true;
                const originalContent = this.deleteBtn.innerHTML;
                this.deleteBtn.innerHTML = `
                    <div class="loading-spinner"></div>
                    <span>Eliminando...</span>
                `;

                const response = await fetch(this.config.urls.delete, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();

                if (data.success) {
                    await Swal.fire({
                        title: '¡Eliminado!',
                        text: data.message,
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    await Swal.fire({
                        title: 'Error',
                        text: data.message,
                        icon: 'error',
                        confirmButtonColor: '#6366f1'
                    });
                    
                    this.deleteBtn.disabled = false;
                    this.deleteBtn.innerHTML = originalContent;
                }
            }

        } catch (error) {
            console.error('Error al eliminar biometría:', error);
            
            await Swal.fire({
                title: 'Error',
                text: 'Error al comunicarse con el servidor',
                icon: 'error',
                confirmButtonColor: '#6366f1'
            });
            
            if (this.deleteBtn) {
                this.deleteBtn.disabled = false;
            }
        }
    }
    
    async toggleFacialLogin() {
        const newState = !this.config.allowLogin;
        const action = newState ? 'activar' : 'desactivar';
        
        try {
            const result = await Swal.fire({
                title: '¿Confirmar cambio?',
                text: `¿Deseas ${action} el login facial?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#6366f1',
                cancelButtonColor: '#6b7280',
                confirmButtonText: 'Sí, continuar',
                cancelButtonText: 'Cancelar'
            });

            if (!result.isConfirmed) {
                return;
            }

            // Deshabilitar botón mientras procesa
            if (this.toggleBtn) {
                this.toggleBtn.disabled = true;
                const originalContent = this.toggleBtn.innerHTML;
                this.toggleBtn.innerHTML = `
                    <div class="loading-spinner"></div>
                    <span>Procesando...</span>
                `;
                
                const response = await fetch(this.config.urls.toggle, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ allow_login: newState })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.config.allowLogin = newState;
                    
                    await Swal.fire({
                        title: '¡Actualizado!',
                        text: data.message,
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    
                    // Recargar después de 1 segundo
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    await Swal.fire({
                        title: 'Error',
                        text: data.message,
                        icon: 'error',
                        confirmButtonColor: '#6366f1'
                    });
                    
                    // Restaurar botón
                    this.toggleBtn.disabled = false;
                    this.toggleBtn.innerHTML = originalContent;
                }
            }
            
        } catch (error) {
            console.error('Error al cambiar estado:', error);
            
            await Swal.fire({
                title: 'Error',
                text: 'Error al comunicarse con el servidor',
                icon: 'error',
                confirmButtonColor: '#6366f1'
            });
            
            // Restaurar botón en caso de error
            if (this.toggleBtn) {
                this.toggleBtn.disabled = false;
            }
        }
    }
    
    drawFaceBox(bbox, confidence) {
        const ctx = this.overlay.getContext('2d');
        ctx.clearRect(0, 0, this.overlay.width, this.overlay.height);
        
        const [x, y, w, h] = bbox;
        
        // Calcular escala entre video y canvas
        const scaleX = this.overlay.width / this.video.videoWidth;
        const scaleY = this.overlay.height / this.video.videoHeight;
        
        const scaledX = x * scaleX;
        const scaledY = y * scaleY;
        const scaledW = w * scaleX;
        const scaledH = h * scaleY;
        
        // Color verde para rostro detectado
        const color = '#10b981';
        
        // Dibujar rectángulo principal
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);
        
        // Dibujar esquinas decorativas
        const cornerLength = 20;
        ctx.lineWidth = 5;
        
        // Superior izquierda
        ctx.beginPath();
        ctx.moveTo(scaledX, scaledY + cornerLength);
        ctx.lineTo(scaledX, scaledY);
        ctx.lineTo(scaledX + cornerLength, scaledY);
        ctx.stroke();
        
        // Superior derecha
        ctx.beginPath();
        ctx.moveTo(scaledX + scaledW - cornerLength, scaledY);
        ctx.lineTo(scaledX + scaledW, scaledY);
        ctx.lineTo(scaledX + scaledW, scaledY + cornerLength);
        ctx.stroke();
        
        // Inferior izquierda
        ctx.beginPath();
        ctx.moveTo(scaledX, scaledY + scaledH - cornerLength);
        ctx.lineTo(scaledX, scaledY + scaledH);
        ctx.lineTo(scaledX + cornerLength, scaledY + scaledH);
        ctx.stroke();
        
        // Inferior derecha
        ctx.beginPath();
        ctx.moveTo(scaledX + scaledW - cornerLength, scaledY + scaledH);
        ctx.lineTo(scaledX + scaledW, scaledY + scaledH);
        ctx.lineTo(scaledX + scaledW, scaledY + scaledH - cornerLength);
        ctx.stroke();
        
        // Texto de confianza
        ctx.fillStyle = color;
        ctx.font = 'bold 16px sans-serif';
        ctx.fillText(
            `${(confidence * 100).toFixed(1)}%`,
            scaledX + 5,
            scaledY - 10
        );
    }
    
    clearOverlay() {
        const ctx = this.overlay.getContext('2d');
        ctx.clearRect(0, 0, this.overlay.width, this.overlay.height);
    }
    
    updateStatus(message, type) {
        if (this.statusText) {
            this.statusText.textContent = message;
        }
        
        if (this.statusIndicator) {
            this.statusIndicator.className = 'status-indicator';
            this.statusIndicator.classList.add(type);
        }
    }
    
    showNotification(type, message) {
        // Mapear tipos a iconos de SweetAlert2
        const iconMap = {
            success: 'success',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };

        Swal.fire({
            icon: iconMap[type] || 'info',
            title: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
    }
    
    destroy() {
        this.stopCamera();
        this.stopDetection();
    }
}

// Función de inicialización global
function initFacialRecognition(config) {
    const manager = new FacialRecognitionManager(config);
    
    // Limpiar cuando se cierre la página
    window.addEventListener('beforeunload', () => {
        manager.destroy();
    });
    
    return manager;
}

// Exportar para uso global
window.FacialRecognitionManager = FacialRecognitionManager;
window.initFacialRecognition = initFacialRecognition;
