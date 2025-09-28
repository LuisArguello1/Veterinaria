/**
 * QR Management Module
 * Funciones para generar, compartir y manejar códigos QR de mascotas
 */

// Función para generar código QR
async function generarQR(mascotaId) {
    try {
        // Mostrar loading con SweetAlert2
        Swal.fire({
            title: 'Generando código QR...',
            html: 'Por favor espera mientras se genera el código QR',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading()
            }
        });

        const response = await fetch(`/mascota/${mascotaId}/qr/generar/`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();
            
            if (data.success) {
                // Cerrar loading y mostrar QR
                Swal.fire({
                    title: '¡Código QR generado!',
                    html: `
                        <div class="text-center">
                            <img src="${data.qr_image}" alt="Código QR" class="mx-auto mb-4 rounded-lg shadow-lg" style="max-width: 300px;">
                            <p class="text-sm text-gray-600 mb-4">Escanea este código desde cualquier celular para ver la información de ${data.mascota_nombre}</p>
                            <div class="flex justify-center">
                                <button onclick="compartirQR('${data.url_publica}', '${data.mascota_nombre}')" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors">
                                    <i class="fas fa-share-alt mr-2"></i>
                                    Compartir Información
                                </button>
                            </div>
                        </div>
                    `,
                    showConfirmButton: false,
                    showCloseButton: true,
                    width: '600px',
                    customClass: {
                        popup: 'qr-modal'
                    }
                });
            } else {
                Swal.fire({
                    title: 'Error',
                    text: data.error || 'Error al generar el código QR',
                    icon: 'error',
                    confirmButtonColor: '#d33'
                });
            }
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error generando QR:', error);
        Swal.fire({
            title: 'Error de conexión',
            text: 'No se pudo generar el código QR. Verifica tu conexión a internet.',
            icon: 'error',
            confirmButtonColor: '#d33'
        });
    }
}

// Función para compartir QR
function compartirQR(url, mascotaNombre) {
    if (navigator.share) {
        // Usar Web Share API si está disponible
        navigator.share({
            title: `Información de ${mascotaNombre}`,
            text: `Mira la información de mi mascota ${mascotaNombre}`,
            url: url
        }).catch((error) => {
            console.log('Error sharing:', error);
            // Fallback a copiar enlace
            copiarEnlace(url);
        });
    } else {
        // Fallback para navegadores que no soportan Web Share API
        copiarEnlace(url);
    }
}

// Función para copiar enlace
function copiarEnlace(url) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(() => {
            Swal.fire({
                title: '¡Enlace copiado!',
                text: 'El enlace se ha copiado al portapapeles',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        }).catch(error => {
            console.error('Error al copiar:', error);
            mostrarEnlaceManual(url);
        });
    } else {
        mostrarEnlaceManual(url);
    }
}

// Función para mostrar enlace manual
function mostrarEnlaceManual(url) {
    Swal.fire({
        title: 'Compartir información',
        html: `
            <p class="mb-4">Copia este enlace para compartir:</p>
            <div class="bg-gray-100 p-3 rounded border break-all text-sm">
                ${url}
            </div>
        `,
        confirmButtonText: 'Cerrar'
    });
}