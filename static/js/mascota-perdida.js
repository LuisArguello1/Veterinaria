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
    // Mostrar modal de confirmación con opción de ubicación
    const { value: formValues } = await Swal.fire({
        title: `¿Reportar ${mascotaNombre} como perdida?`,
        html: `
            <div class="text-left mb-4">
                <p class="text-gray-700 mb-4">
                    Al confirmar, se enviará una alerta a todos los usuarios registrados 
                    para ayudar en la búsqueda de ${mascotaNombre}.
                </p>
                <label for="ubicacion-perdida" class="block text-sm font-medium text-gray-700 mb-2">
                    Ubicación donde se perdió (opcional):
                </label>
                <input 
                    id="ubicacion-perdida" 
                    type="text" 
                    class="swal2-input w-full" 
                    placeholder="Ej: Cerca del parque central, Barrio Los Álamos..."
                    maxlength="255">
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Sí, reportar como perdida',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#6b7280',
        preConfirm: () => {
            return {
                ubicacion: document.getElementById('ubicacion-perdida').value.trim()
            };
        }
    });

    if (formValues) {
        // Mostrar loading
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
            if (formValues.ubicacion) {
                formData.append('ubicacion_perdida', formValues.ubicacion);
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