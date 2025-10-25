/**
 * Sistema de Login Facial
 * Maneja el reconocimiento facial para inicio de sesión
 */
class FacialLoginSystem {
    constructor(verifyUrl) {
        this.verifyUrl = verifyUrl;
        this.modal = document.getElementById('facialLoginModal');
        this.video = document.getElementById('facialLoginVideo');
        this.overlay = document.getElementById('facialLoginOverlay');
        this.statusText = document.getElementById('facialLoginStatusText');
        this.statusIndicator = this.statusText?.previousElementSibling;
        
        this.stream = null;
        this.isProcessing = false;
        this.detectionInterval = null;
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        document.getElementById('facialLoginBtn')?.addEventListener('click', () => this.openModal());
        document.getElementById('closeFacialModal')?.addEventListener('click', () => this.closeModal());
        document.getElementById('cancelFacialLogin')?.addEventListener('click', () => this.closeModal());
        document.getElementById('retryFacialLogin')?.addEventListener('click', () => this.startDetection());
    }
    
    async openModal() {
        this.modal.classList.add('show');
        await this.startCamera();
        this.startDetection();
    }
    
    closeModal() {
        this.modal.classList.remove('show');
        this.stopCamera();
        this.stopDetection();
    }
    
    async startCamera() {
        try {
            this.updateStatus('Iniciando cámara...', 'yellow');
            
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = this.stream;
            
            // Ajustar canvas al tamaño del video
            this.video.addEventListener('loadedmetadata', () => {
                this.overlay.width = this.video.videoWidth;
                this.overlay.height = this.video.videoHeight;
            });
            
            this.updateStatus('Cámara iniciada. Buscando rostro...', 'yellow');
        } catch (error) {
            console.error('Error al acceder a la cámara:', error);
            this.updateStatus('Error al acceder a la cámara. Verifica los permisos.', 'red');
        }
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }
    
    startDetection() {
        this.stopDetection();
        document.getElementById('retryFacialLogin').style.display = 'none';
        
        this.detectionInterval = setInterval(() => {
            if (!this.isProcessing) {
                this.captureAndVerify();
            }
        }, 1000); // Verificar cada segundo
    }
    
    stopDetection() {
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
    }
    
    async captureAndVerify() {
        if (this.isProcessing || !this.video.videoWidth) return;
        
        this.isProcessing = true;
        
        try {
            // Capturar frame del video
            const canvas = document.createElement('canvas');
            canvas.width = this.video.videoWidth;
            canvas.height = this.video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(this.video, 0, 0);
            
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Enviar al servidor para verificación
            const response = await fetch(this.verifyUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateStatus(`✓ ${data.message}`, 'green');
                this.drawFaceBox(data.similarity || 1.0);
                
                // Redirigir al dashboard
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1000);
            } else {
                // Continuar buscando
                this.updateStatus(data.message || 'Buscando rostro...', 'yellow');
            }
        } catch (error) {
            console.error('Error en verificación:', error);
            this.updateStatus('Error al verificar. Reintentando...', 'red');
        } finally {
            this.isProcessing = false;
        }
    }
    
    drawFaceBox(confidence) {
        const ctx = this.overlay.getContext('2d');
        ctx.clearRect(0, 0, this.overlay.width, this.overlay.height);
        
        // Dibujar cuadro verde en el centro
        const boxWidth = this.overlay.width * 0.5;
        const boxHeight = this.overlay.height * 0.6;
        const x = (this.overlay.width - boxWidth) / 2;
        const y = (this.overlay.height - boxHeight) / 2;
        
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, boxWidth, boxHeight);
        
        // Esquinas decorativas
        const cornerLength = 30;
        ctx.lineWidth = 6;
        
        // Superior izquierda
        ctx.beginPath();
        ctx.moveTo(x, y + cornerLength);
        ctx.lineTo(x, y);
        ctx.lineTo(x + cornerLength, y);
        ctx.stroke();
        
        // Superior derecha
        ctx.beginPath();
        ctx.moveTo(x + boxWidth - cornerLength, y);
        ctx.lineTo(x + boxWidth, y);
        ctx.lineTo(x + boxWidth, y + cornerLength);
        ctx.stroke();
        
        // Inferior izquierda
        ctx.beginPath();
        ctx.moveTo(x, y + boxHeight - cornerLength);
        ctx.lineTo(x, y + boxHeight);
        ctx.lineTo(x + cornerLength, y + boxHeight);
        ctx.stroke();
        
        // Inferior derecha
        ctx.beginPath();
        ctx.moveTo(x + boxWidth - cornerLength, y + boxHeight);
        ctx.lineTo(x + boxWidth, y + boxHeight);
        ctx.lineTo(x + boxWidth, y + boxHeight - cornerLength);
        ctx.stroke();
    }
    
    updateStatus(message, color) {
        if (this.statusText) {
            this.statusText.textContent = message;
        }
        
        if (this.statusIndicator) {
            this.statusIndicator.className = 'w-3 h-3 rounded-full';
            
            switch(color) {
                case 'green':
                    this.statusIndicator.classList.add('bg-green-400');
                    break;
                case 'red':
                    this.statusIndicator.classList.add('bg-red-400');
                    break;
                default:
                    this.statusIndicator.classList.add('bg-yellow-400', 'animate-pulse');
            }
        }
    }
}

// Exportar para uso global
window.FacialLoginSystem = FacialLoginSystem;
