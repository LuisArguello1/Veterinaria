/**
 * Biometria Management Module
 * Funciones para entrenar modelos y eliminar datos biométricos
 */

// Función para entrenar modelo de biometría
async function entrenarModelo(mascotaId) {
        if (!mascotaId) {
            Swal.fire({
                title: 'Error',
                text: 'No se pudo obtener el ID de la mascota',
                icon: 'error',
                confirmButtonColor: '#d33'
            });
            return;
        }
        
        const result = await Swal.fire({
            title: '¿Activar reconocimiento facial?',
            text: 'Este proceso puede tardar unos minutos. ¿Deseas continuar?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, activar',
            cancelButtonText: 'Cancelar'
        });
        
        if (!result.isConfirmed) {
            return;
        }
        
        // Buscar el botón específico de esta mascota
        const botonEntrenar = document.querySelector(`button[onclick="entrenarModelo(${mascotaId})"]`);
        
        try {
            // Mostrar estado de carga
            if (botonEntrenar) {
                botonEntrenar.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Activando...';
                botonEntrenar.disabled = true;
            }
            
            const response = await fetch(`/mascota/train-model/${mascotaId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    let mensaje = `Reconocimiento activado correctamente en ${data.tiempo}s`;
                    if (data.confianza) {
                        mensaje += `<br><strong>Confianza:</strong> ${(data.confianza * 100).toFixed(1)}%`;
                    }
                    if (data.num_imagenes) {
                        mensaje += `<br><strong>Imágenes procesadas:</strong> ${data.num_imagenes}`;
                    }
                    
                    Swal.fire({
                        title: 'Activacion de reconocimiento exitoso!',
                        html: mensaje,
                        icon: 'success',
                        confirmButtonColor: '#10b981',
                        confirmButtonText: 'Entendido'
                    }).then(() => {
                        // Recargar la página para actualizar el estado
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        title: 'Error en la activacion',
                        text: data.error || 'Error al entrenar el modelo',
                        icon: 'error',
                        confirmButtonColor: '#d33'
                    });
                    console.error('Error details:', data);
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                alert(errorData.error || 'Error al entrenar el modelo');
                console.error('HTTP Error:', response.status, errorData);
            }
        } catch (err) {
            console.error('Error al entrenar el modelo:', err);
            alert('Error de conexión al entrenar el modelo');
        } finally {
            // Restaurar botón
            if (botonEntrenar) {
                botonEntrenar.innerHTML = '<i class="fas fa-brain mr-1"></i> Activar reconocimiento';
                botonEntrenar.disabled = false;
            }
        }
    }

// Función para eliminar biometría
async function eliminarBiometria(mascotaId, mascotaNombre) {
    try {
        const result = await Swal.fire({
            title: '¿Eliminar datos biométricos?',
            html: `
                <div class="text-left">
                    <p class="mb-3">Esta acción eliminará todos los datos biométricos de <strong>${mascotaNombre}</strong>.</p>
                    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                                </svg>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm text-yellow-700">
                                    <strong>Advertencia:</strong> Esta acción no se puede deshacer.
                                </p>
                            </div>
                        </div>
                    </div>
                    <p class="text-sm text-gray-600">Tendrás que volver a registrar las fotos biométricas si deseas usar el reconocimiento facial.</p>
                </div>
            `,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc2626',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            width: '500px'
        });

        if (result.isConfirmed) {
            // Mostrar loading
            Swal.fire({
                title: 'Eliminando datos...',
                html: 'Eliminando datos biométricos, por favor espera...',
                allowOutsideClick: false,
                showConfirmButton: false,
                willOpen: () => {
                    Swal.showLoading()
                }
            });

            const response = await fetch(`/mascota/${mascotaId}/delete-biometria/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                Swal.fire({
                    title: '¡Datos eliminados!',
                    text: 'Los datos biométricos han sido eliminados correctamente',
                    icon: 'success',
                    confirmButtonColor: '#10b981'
                }).then(() => {
                    // Recargar la página para actualizar la información
                    window.location.reload();
                });
            } else {
                console.error('Error response:', response.status, response.statusText);
                const errorText = await response.text();
                console.error('Error details:', errorText);
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
        }
    } catch (error) {
        console.error('Error eliminando biometría:', error);
        Swal.fire({
            title: 'Error',
            text: `No se pudieron eliminar los datos biométricos: ${error.message}`,
            icon: 'error',
            confirmButtonColor: '#dc2626'
        });
    }
}