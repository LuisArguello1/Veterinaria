/**
 * Mascota Management Module
 * Funciones para manejo general de mascotas (eliminar, etc.)
 */

// Función para eliminar mascota
// Función para eliminar mascota completa
    async function eliminarMascota(mascotaId, mascotaNombre) {
        const result = await Swal.fire({
            title: '¿Eliminar mascota?',
            html: `¿Estás seguro de que deseas eliminar a <strong>${mascotaNombre}</strong>?<br><br>
                   <span class="text-red-600"><i class="fas fa-exclamation-triangle"></i> Esta acción eliminará:</span><br>
                   • Todos los datos de la mascota<br>
                   • Todas las imágenes y fotos<br>
                   • Todos los datos biométricos<br>
                   • Registros de reconocimiento<br><br>
                   <strong>Esta acción no se puede deshacer.</strong>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc2626',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });

        if (result.isConfirmed) {
            try {
                const url = `/mascota/${mascotaId}/delete/`;
                console.log('URL a llamar:', url);
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                });

                if (response.ok) {
                    Swal.fire({
                        title: '¡Eliminado!',
                        text: `${mascotaNombre} ha sido eliminado exitosamente.`,
                        icon: 'success',
                        confirmButtonColor: '#10b981'
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    console.error('Error response:', response.status, response.statusText);
                    const errorText = await response.text();
                    console.error('Error details:', errorText);
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
            } catch (error) {
                console.error('Error eliminando mascota:', error);
                Swal.fire({
                    title: 'Error',
                    text: `No se pudo eliminar la mascota: ${error.message}`,
                    icon: 'error',
                    confirmButtonColor: '#dc2626'
                });
            }
        }
    }