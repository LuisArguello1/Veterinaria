// Funciones para editar mascota
    window.editarMascota = function(mascotaId) {
        // Obtener datos actuales de la mascota
        fetch(`/mascota/${mascotaId}/editar/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Llenar el formulario con los datos actuales
                const mascotaData = data.mascota_data;
                
                document.getElementById('edit-mascota-name').textContent = mascotaData.nombre;
                document.getElementById('edit_nombre').value = mascotaData.nombre;
                document.getElementById('edit_raza').value = mascotaData.raza;
                document.getElementById('edit_sexo').value = mascotaData.sexo;
                document.getElementById('edit_edad').value = mascotaData.edad;
                document.getElementById('edit_edad_unidad').value = mascotaData.edad_unidad;
                document.getElementById('edit_peso').value = mascotaData.peso;
                document.getElementById('edit_color').value = mascotaData.color;
                document.getElementById('edit_estado_corporal').value = mascotaData.estado_corporal;
                document.getElementById('edit_etapa_vida').value = mascotaData.etapa_vida;
                document.getElementById('edit_fecha_nacimiento').value = mascotaData.fecha_nacimiento;
                document.getElementById('edit_caracteristicas_especiales').value = mascotaData.caracteristicas_especiales;
                
                // Mostrar foto actual si existe
                const currentPhotoPreview = document.getElementById('current-photo-preview');
                const currentPhotoImg = document.getElementById('current-photo-img');
                if (mascotaData.foto_perfil_url) {
                    currentPhotoImg.src = mascotaData.foto_perfil_url;
                    currentPhotoPreview.classList.remove('hidden');
                } else {
                    currentPhotoPreview.classList.add('hidden');
                }
                
                // Guardar el ID de la mascota en el formulario
                document.getElementById('editarMascotaForm').dataset.mascotaId = mascotaId;
                
                // Mostrar el modal
                document.getElementById('editarMascotaModal').classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar los datos de la mascota');
        });
    };
    
    window.cerrarModalEditar = function() {
        document.getElementById('editarMascotaModal').classList.add('hidden');
        document.getElementById('editarMascotaForm').reset();
    };
    
    // Manejar envío del formulario de edición
    document.getElementById('editarMascotaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const mascotaId = this.dataset.mascotaId;
        const guardarBtn = document.getElementById('guardar-cambios-btn');
        const guardarBtnText = document.getElementById('guardar-btn-text');
        
        // Deshabilitar botón y mostrar loading
        guardarBtn.disabled = true;
        guardarBtnText.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Guardando...';
        
        const formData = new FormData(this);
        
        fetch(`/mascota/${mascotaId}/editar/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar los datos en la interfaz
                actualizarDatosMascotaEnInterfaz(mascotaId, data.mascota_data);
                
                // Cerrar modal y mostrar mensaje de éxito
                cerrarModalEditar();
                Swal.fire({
                    title: '¡Éxito!',
                    text: data.message,
                    icon: 'success',
                    confirmButtonColor: '#3B82F6'
                });
            } else {
                // Mostrar errores
                let errorMessage = data.message || 'Error al actualizar la mascota';
                if (data.errors) {
                    const errorList = Object.entries(data.errors)
                        .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
                        .join('\n');
                    errorMessage += '\n\n' + errorList;
                }
                
                Swal.fire({
                    title: 'Error',
                    text: errorMessage,
                    icon: 'error',
                    confirmButtonColor: '#EF4444'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error',
                text: 'Error de conexión al actualizar la mascota',
                icon: 'error',
                confirmButtonColor: '#EF4444'
            });
        })
        .finally(() => {
            // Rehabilitar botón
            guardarBtn.disabled = false;
            guardarBtnText.innerHTML = '<i class="fas fa-save mr-1"></i>Guardar Cambios';
        });
    });
    
    function actualizarDatosMascotaEnInterfaz(mascotaId, mascotaData) {
        // Función auxiliar para encontrar elementos por texto
        function findElementByText(container, text) {
            const walker = document.createTreeWalker(
                container,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                if (node.textContent.includes(text)) {
                    return node.parentElement;
                }
            }
            return null;
        }
        
        // Actualizar el nombre en el título
        const nombreElement = document.querySelector(`#mascota-${mascotaId} h1`);
        if (nombreElement) {
            nombreElement.textContent = mascotaData.nombre;
        }
        
        // Actualizar todos los campos de información
        const mascotaContainer = document.getElementById(`mascota-${mascotaId}`);
        if (mascotaContainer) {
            // Actualizar raza
            const razaElement = findElementByText(mascotaContainer, 'Especie/Raza:');
            if (razaElement) {
                razaElement.innerHTML = '<span class="font-medium text-gray-700">Especie/Raza:</span> ' + mascotaData.raza;
            }
            
            // Actualizar edad
            const edadElement = findElementByText(mascotaContainer, 'Edad:');
            if (edadElement) {
                edadElement.innerHTML = '<span class="font-medium text-gray-700">Edad:</span> ' + mascotaData.edad_completa;
            }
            
            // Actualizar sexo
            const sexoElement = findElementByText(mascotaContainer, 'Sexo:');
            if (sexoElement) {
                sexoElement.innerHTML = '<span class="font-medium text-gray-700">Sexo:</span> ' + mascotaData.sexo;
            }
            
            // Actualizar etapa de vida
            const etapaElement = findElementByText(mascotaContainer, 'Etapa de vida:');
            if (etapaElement) {
                etapaElement.innerHTML = '<span class="font-medium text-gray-700">Etapa de vida:</span> ' + mascotaData.etapa_vida;
            }
            
            // Actualizar estado corporal
            const estadoElement = findElementByText(mascotaContainer, 'Estado corporal:');
            if (estadoElement) {
                estadoElement.innerHTML = '<span class="font-medium text-gray-700">Estado corporal:</span> ' + mascotaData.estado_corporal;
            }
            
            // Actualizar peso
            const pesoElement = findElementByText(mascotaContainer, 'Peso:');
            if (pesoElement) {
                pesoElement.innerHTML = '<span class="font-medium text-gray-700">Peso:</span> ' + mascotaData.peso;
            }
            
            // Actualizar foto si hay una nueva
            if (mascotaData.foto_perfil_url) {
                const fotoElement = mascotaContainer.querySelector('img');
                if (fotoElement) {
                    fotoElement.src = mascotaData.foto_perfil_url;
                }
            }
            
            // Actualizar información detallada en la sección de detalles
            const detallesContainer = mascotaContainer.querySelector('dl');
            if (detallesContainer) {
                // Color
                if (mascotaData.color) {
                    const colorDt = Array.from(detallesContainer.querySelectorAll('dt')).find(dt => dt.textContent.includes('Color'));
                    if (colorDt && colorDt.nextElementSibling) {
                        colorDt.nextElementSibling.textContent = mascotaData.color;
                    }
                }
                
                // Fecha de nacimiento
                if (mascotaData.fecha_nacimiento) {
                    const fechaDt = Array.from(detallesContainer.querySelectorAll('dt')).find(dt => dt.textContent.includes('Fecha de nacimiento'));
                    if (fechaDt && fechaDt.nextElementSibling) {
                        fechaDt.nextElementSibling.textContent = mascotaData.fecha_nacimiento;
                    }
                }
                
                // Características especiales
                if (mascotaData.caracteristicas_especiales) {
                    const caracteristicasDt = Array.from(detallesContainer.querySelectorAll('dt')).find(dt => dt.textContent.includes('Características especiales'));
                    if (caracteristicasDt && caracteristicasDt.nextElementSibling) {
                        caracteristicasDt.nextElementSibling.textContent = mascotaData.caracteristicas_especiales;
                    }
                }
            }
        }
        
        // Recargar la página después de un breve delay para asegurar que todos los cambios se reflejen
        setTimeout(() => {
            location.reload();
        }, 1500);
    }