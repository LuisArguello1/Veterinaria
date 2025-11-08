/**
 * JavaScript para el sistema de mascotas perdidas
 * Maneja reportes de perdida y encontrada
 */

/**
 * Reporta una mascota como perdida
 * @param {number} mascotaId - ID de la mascota
 * @param {string} mascotaNombre - Nombre de la mascota
 */
async function reportarMascotaPerdida(mascotaId, mascotaNombre) {
    // Mostrar modal de confirmación con opción de ubicación y geolocalización
    const { value: formValues } = await Swal.fire({
        title: `¿Reportar ${mascotaNombre} como perdida?`,
        html: `
            <div class="text-left mb-4">
                <p class="text-gray-700 mb-4">
                    Al confirmar, se enviará una alerta a todos los usuarios registrados 
                    para ayudar en la búsqueda de ${mascotaNombre}.
                </p>
                <label for="ubicacion-perdida" class="block text-sm font-medium text-gray-700 mb-2">
                    Ubicación donde se perdió:
                </label>
                <input 
                    id="ubicacion-perdida" 
                    type="text" 
                    class="swal2-input w-full" 
                    placeholder="Ej: Cerca del parque central, Barrio Los Álamos..."
                    maxlength="255"
                    required>
                
                <div class="mt-4">
                    <label class="flex items-center justify-center gap-2 cursor-pointer">
                        <input 
                            type="checkbox" 
                            id="usar-ubicacion-actual" 
                            class="w-5 h-5 text-blue-600 rounded"
                            checked>
                        <span class="text-sm text-gray-700">
                            <i class="fas fa-map-marker-alt text-blue-500"></i>
                            Usar mi ubicación actual para mostrar en el mapa
                        </span>
                    </label>
                    <p class="text-xs text-gray-500 mt-2 text-center">
                        Esto ayudará a otros usuarios a ver dónde se perdió tu mascota
                    </p>
                </div>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Sí, reportar como perdida',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#6b7280',
        preConfirm: () => {
            const ubicacion = document.getElementById('ubicacion-perdida').value.trim();
            const usarUbicacion = document.getElementById('usar-ubicacion-actual').checked;
            
            if (!ubicacion) {
                Swal.showValidationMessage('Por favor, describe dónde se perdió tu mascota');
                return false;
            }
            
            return {
                ubicacion: ubicacion,
                usarUbicacion: usarUbicacion
            };
        }
    });

    if (formValues) {
        // Si el usuario quiere usar su ubicación actual, obtenerla primero
        let coordenadas = null;
        
        if (formValues.usarUbicacion) {
            // Mostrar loading mientras obtenemos ubicación
            Swal.fire({
                title: 'Obteniendo ubicación...',
                html: 'Por favor, permite el acceso a tu ubicación',
                allowOutsideClick: false,
                showConfirmButton: false,
                willOpen: () => {
                    Swal.showLoading();
                }
            });
            
            try {
                coordenadas = await obtenerUbicacionActual();
                console.log('📍 Ubicación obtenida:', coordenadas);
            } catch (error) {
                console.error('Error obteniendo ubicación:', error);
                // Continuar sin ubicación si hay error
                const continuarSinUbicacion = await Swal.fire({
                    title: 'No se pudo obtener ubicación',
                    text: '¿Deseas continuar sin agregar la ubicación al mapa?',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, continuar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#dc2626',
                    cancelButtonColor: '#6b7280'
                });
                
                if (!continuarSinUbicacion.isConfirmed) {
                    return;
                }
            }
        }
        
        // Mostrar loading final
        Swal.fire({
            title: 'Reportando mascota perdida...',
            html: 'Enviando alertas a todos los usuarios...',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });

        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            formData.append('ubicacion_perdida', formValues.ubicacion);
            
            // Agregar coordenadas si se obtuvieron
            if (coordenadas) {
                formData.append('latitud', coordenadas.lat);
                formData.append('longitud', coordenadas.lng);
                console.log('📤 Enviando coordenadas:', coordenadas);
            }

            const response = await fetch(`/mascota/${mascotaId}/reportar-perdida/`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                await Swal.fire({
                    title: '¡Reporte exitoso!',
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#10b981'
                });

                // Actualizar la interfaz
                actualizarBotonPerdida(mascotaId, true, mascotaNombre);
                
                // Recargar la página para mostrar cambios
                location.reload();
            } else {
                await Swal.fire({
                    title: 'Error',
                    text: data.error || 'No se pudo reportar la mascota como perdida',
                    icon: 'error',
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc2626'
                });
            }
        } catch (error) {
            console.error('Error reportando mascota perdida:', error);
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
 * Cancela el reporte de mascota perdida
 * @param {number} mascotaId - ID de la mascota
 * @param {string} mascotaNombre - Nombre de la mascota
 */
async function cancelarReportePerdida(mascotaId, mascotaNombre) {
    const result = await Swal.fire({
        title: `¿Cancelar reporte de ${mascotaNombre}?`,
        text: 'Esta acción eliminará el estado de "perdida" de tu mascota.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, cancelar reporte',
        cancelButtonText: 'No cancelar',
        confirmButtonColor: '#059669',
        cancelButtonColor: '#6b7280'
    });

    if (result.isConfirmed) {
        // Mostrar loading
        Swal.fire({
            title: 'Cancelando reporte...',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });

        try {
            const response = await fetch(`/mascota/${mascotaId}/cancelar-perdida/`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            const data = await response.json();

            if (data.success) {
                await Swal.fire({
                    title: '¡Reporte cancelado!',
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#10b981'
                });

                // Actualizar la interfaz
                actualizarBotonPerdida(mascotaId, false, mascotaNombre);
                
                // Recargar la página para mostrar cambios
                location.reload();
            } else {
                await Swal.fire({
                    title: 'Error',
                    text: data.error || 'No se pudo cancelar el reporte',
                    icon: 'error',
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc2626'
                });
            }
        } catch (error) {
            console.error('Error cancelando reporte:', error);
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
 * Reporta una mascota como encontrada (desde QR público)
 * @param {string} mascotaUuid - UUID de la mascota
 * @param {string} mascotaNombre - Nombre de la mascota
 */
async function reportarMascotaEncontrada(mascotaUuid, mascotaNombre) {
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
        // Mostrar loading
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
                    'Content-Type': 'application/json'
                }
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
                
                // Recargar la página para actualizar el estado
                location.reload();
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
 * Obtiene la ubicación actual del usuario usando Geolocation API
 * @returns {Promise<Object>} Objeto con lat y lng
 */
function obtenerUbicacionActual() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocalización no disponible en este navegador'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log('📍 Ubicación obtenida:', {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
                resolve({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
            },
            (error) => {
                console.error('❌ Error de geolocalización:', error);
                let errorMessage = 'Error obteniendo ubicación';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Permiso de ubicación denegado. Por favor, permite el acceso a tu ubicación en la configuración del navegador.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Ubicación no disponible. Asegúrate de que el GPS esté activado.';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Tiempo de espera agotado obteniendo ubicación precisa. Intenta de nuevo.';
                        break;
                }
                reject(new Error(errorMessage));
            },
            {
                enableHighAccuracy: true, // Forzar uso de GPS para mayor precisión
                timeout: 20000, // 20 segundos para dar tiempo al GPS
                maximumAge: 0 // NO usar ubicación cacheada, siempre obtener nueva
            }
        );
    });
}

/**
 * Verifica el estado de perdida de una mascota
 * @param {string} mascotaUuid - UUID de la mascota
 * @returns {Promise<Object>} Estado de la mascota
 */
async function verificarEstadoPerdida(mascotaUuid) {
    try {
        const response = await fetch(`/perdida/${mascotaUuid}/verificar-estado/`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error verificando estado de perdida:', error);
        return { success: false, error: 'Error de conexión' };
    }
}

/**
 * Actualiza el botón de perdida en la interfaz
 * @param {number} mascotaId - ID de la mascota
 * @param {boolean} perdida - Si está perdida o no
 * @param {string} nombre - Nombre de la mascota
 */
function actualizarBotonPerdida(mascotaId, perdida, nombre) {
    // Buscar el contenedor de botones de la mascota
    const contenedorBotones = document.querySelector(`#mascota-${mascotaId} .grid.grid-cols-2.sm\\:grid-cols-4`);
    if (!contenedorBotones) return;

    // Buscar botón existente de perdida
    let botonPerdida = contenedorBotones.querySelector('.btn-perdida, .btn-cancelar-perdida');
    
    if (perdida) {
        // Crear/actualizar botón para cancelar perdida
        if (botonPerdida) {
            botonPerdida.outerHTML = crearBotonCancelarPerdida(mascotaId, nombre);
        } else {
            // Agregar nuevo botón
            contenedorBotones.insertAdjacentHTML('beforeend', crearBotonCancelarPerdida(mascotaId, nombre));
        }
    } else {
        // Crear/actualizar botón para reportar perdida
        if (botonPerdida) {
            botonPerdida.outerHTML = crearBotonReportarPerdida(mascotaId, nombre);
        } else {
            // Agregar nuevo botón
            contenedorBotones.insertAdjacentHTML('beforeend', crearBotonReportarPerdida(mascotaId, nombre));
        }
    }
}

/**
 * Crea el HTML para el botón de reportar perdida
 * @param {number} mascotaId - ID de la mascota
 * @param {string} nombre - Nombre de la mascota
 * @returns {string} HTML del botón
 */
function crearBotonReportarPerdida(mascotaId, nombre) {
    return `
        <button onclick="reportarMascotaPerdida(${mascotaId}, '${nombre}')" 
            class="btn-perdida inline-flex items-center justify-center px-3 py-2 border border-orange-300 text-sm font-medium rounded-md shadow-sm text-orange-600 bg-white hover:bg-orange-50 hover:border-orange-400">
            <i class="fas fa-exclamation-triangle mr-1"></i> Reportar perdida
        </button>
    `;
}

/**
 * Crea el HTML para el botón de cancelar perdida
 * @param {number} mascotaId - ID de la mascota
 * @param {string} nombre - Nombre de la mascota
 * @returns {string} HTML del botón
 */
function crearBotonCancelarPerdida(mascotaId, nombre) {
    return `
        <button onclick="cancelarReportePerdida(${mascotaId}, '${nombre}')" 
            class="btn-cancelar-perdida inline-flex items-center justify-center px-3 py-2 border border-green-300 text-sm font-medium rounded-md shadow-sm text-green-600 bg-white hover:bg-green-50 hover:border-green-400">
            <i class="fas fa-check-circle mr-1"></i> Cancelar perdida
        </button>
    `;
}

// Exportar funciones para uso externo
window.mascotaPerdidaUtils = {
    reportar: reportarMascotaPerdida,
    cancelar: cancelarReportePerdida,
    encontrada: reportarMascotaEncontrada,
    verificarEstado: verificarEstadoPerdida,
    actualizarBoton: actualizarBotonPerdida
};