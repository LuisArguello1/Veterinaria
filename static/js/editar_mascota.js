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
        .then(response => {
            // Verificar si la respuesta es JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`El servidor respondió con HTML en lugar de JSON al cargar datos. Status: ${response.status}`);
            }
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || `Error del servidor: ${response.status}`);
                });
            }
            
            return response.json();
        })
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
            console.error('Error al cargar datos:', error);
            console.error('Mensaje:', error.message);
            
            let errorMessage = 'Error al cargar los datos de la mascota';
            
            if (error.message.includes('HTML en lugar de JSON')) {
                errorMessage = 'Error en el servidor al cargar los datos. El servidor está devolviendo una página de error. Revisa los logs del servidor.';
            } else {
                errorMessage = error.message;
            }
            
            Swal.fire({
                title: 'Error',
                text: errorMessage,
                icon: 'error',
                confirmButtonColor: '#EF4444',
                footer: 'Revisa la consola del navegador (F12) y los logs del servidor para más detalles'
            });
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
        
        // Limpiar errores previos
        document.querySelectorAll('.border-red-500').forEach(el => el.classList.remove('border-red-500'));
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        
        let hayErrores = false;
        
        // Función para mostrar error en input
        function mostrarError(input, mensaje) {
            input.classList.add('border-red-500');
            const errorDiv = document.createElement('p');
            errorDiv.className = 'error-message text-xs text-red-600 mt-1';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i>${mensaje}`;
            input.parentElement.appendChild(errorDiv);
            hayErrores = true;
        }
        
        // ✅ VALIDACIÓN: Verificar edad
        const edadInput = document.getElementById('edit_edad');
        const edadValue = parseFloat(edadInput.value);
        if (isNaN(edadValue) || edadValue <= 0 || edadValue > 30) {
            mostrarError(edadInput, `La edad debe estar entre 0 y 30 (ingresaste: ${edadValue || 'vacío'})`);
        }
        
        // ✅ VALIDACIÓN: Verificar peso
        const pesoInput = document.getElementById('edit_peso');
        const pesoValue = parseFloat(pesoInput.value);
        if (isNaN(pesoValue) || pesoValue < 0.1 || pesoValue > 200) {
            mostrarError(pesoInput, `El peso debe estar entre 0.1 kg y 200 kg (ingresaste: ${pesoValue || 'vacío'} kg)`);
        }
        
        // ✅ VALIDACIÓN: Verificar coherencia entre fecha de nacimiento y edad
        const fechaNacimientoInput = document.getElementById('edit_fecha_nacimiento');
        const edadUnidadInput = document.getElementById('edit_edad_unidad');
        
        if (fechaNacimientoInput.value && !isNaN(edadValue) && edadValue > 0) {
            const fechaNac = new Date(fechaNacimientoInput.value);
            const hoy = new Date();
            const unidad = edadUnidadInput.value;
            
            // Calcular edad desde fecha de nacimiento
            let edadCalculadaAnios = hoy.getFullYear() - fechaNac.getFullYear();
            const mesActual = hoy.getMonth();
            const mesNacimiento = fechaNac.getMonth();
            
            if (mesActual < mesNacimiento || (mesActual === mesNacimiento && hoy.getDate() < fechaNac.getDate())) {
                edadCalculadaAnios--;
            }
            
            let mesesAdicionales = mesActual - mesNacimiento;
            if (mesesAdicionales < 0) {
                mesesAdicionales += 12;
            }
            
            const edadCalculadaTotalAnios = edadCalculadaAnios + (mesesAdicionales / 12);
            let edadIngresadaEnAnios = edadValue;
            if (unidad === 'meses') {
                edadIngresadaEnAnios = edadValue / 12;
            }
            
            const diferencia = Math.abs(edadIngresadaEnAnios - edadCalculadaTotalAnios);
            
            // Si la diferencia es mayor a 3 meses, mostrar error
            if (diferencia > 0.25) {
                let textoEdadIngresada = unidad === 'años' ? `${edadValue} año${edadValue !== 1 ? 's' : ''}` : `${edadValue} mes${edadValue !== 1 ? 'es' : ''}`;
                let textoEdadCalculada = `${edadCalculadaAnios} año${edadCalculadaAnios !== 1 ? 's' : ''} y ${mesesAdicionales} mes${mesesAdicionales !== 1 ? 'es' : ''}`;
                
                mostrarError(edadInput, `La edad (${textoEdadIngresada}) no coincide con la fecha de nacimiento (${textoEdadCalculada})`);
                mostrarError(fechaNacimientoInput, `Verifica que la fecha coincida con la edad ingresada`);
            }
        }
        
        // ✅ VALIDACIÓN: Verificar tamaño de imagen
        const fotoInput = document.getElementById('edit_foto_perfil');
        if (fotoInput && fotoInput.files.length > 0) {
            const file = fotoInput.files[0];
            const maxSize = 5 * 1024 * 1024;
            
            if (file.size > maxSize) {
                mostrarError(fotoInput, `Imagen muy grande: ${(file.size / 1024 / 1024).toFixed(2)} MB (máximo 5 MB)`);
            }
            
            if (!file.type.startsWith('image/')) {
                mostrarError(fotoInput, `Debe ser una imagen (JPG, PNG, etc.)`);
            }
        }
        
        // Si hay errores, no enviar
        if (hayErrores) {
            return;
        }
        
        // ✅ SI TODO ESTÁ BIEN: Proceder con el guardado
        guardarBtn.disabled = true;
        guardarBtnText.textContent = 'Guardando...';

        
        const formData = new FormData(this);
        
        fetch(`/mascota/${mascotaId}/editar/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            // Verificar si la respuesta es JSON antes de parsear
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`El servidor respondió con HTML en lugar de JSON. Status: ${response.status}`);
            }
            
            // Si el status no es OK, lanzar error con el status
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || `Error del servidor: ${response.status}`);
                });
            }
            
            return response.json();
        })
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
                // Mostrar errores con mejor formato
                let errorMessage = data.message || 'Error al actualizar la mascota';
                let errorHtml = '<div class="text-left">';
                
                if (data.errors) {
                    errorHtml += '<p class="mb-3">' + errorMessage + '</p>';
                    errorHtml += '<div class="space-y-2">';
                    
                    // Mapeo de nombres de campos a etiquetas amigables
                    const fieldLabels = {
                        'nombre': 'Nombre',
                        'raza': 'Raza',
                        'edad': 'Edad',
                        'peso': 'Peso',
                        'fecha_nacimiento': 'Fecha de Nacimiento',
                        'color': 'Color',
                        'sexo': 'Sexo',
                        'etapa_vida': 'Etapa de Vida',
                        'estado_corporal': 'Estado Corporal',
                        'caracteristicas_especiales': 'Características Especiales',
                        '__all__': 'Error General'
                    };
                    
                    Object.entries(data.errors).forEach(([field, errors]) => {
                        const fieldLabel = fieldLabels[field] || field;
                        errors.forEach(error => {
                            errorHtml += `
                                <div class="bg-red-50 border-l-4 border-red-400 p-3 rounded">
                                    <p class="text-sm">
                                        <strong class="text-red-800">${fieldLabel}:</strong>
                                        <span class="text-red-700">${error}</span>
                                    </p>
                                </div>
                            `;
                        });
                    });
                    
                    errorHtml += '</div></div>';
                    
                    Swal.fire({
                        title: 'Error de Validación',
                        html: errorHtml,
                        icon: 'error',
                        confirmButtonColor: '#EF4444',
                        width: '600px'
                    });
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: errorMessage,
                        icon: 'error',
                        confirmButtonColor: '#EF4444'
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error completo:', error);
            console.error('Mensaje de error:', error.message);
            
            let errorMessage = 'Error de conexión al actualizar la mascota';
            
            // Determinar el tipo de error
            if (error.message.includes('HTML en lugar de JSON')) {
                errorMessage = 'Error en el servidor. Por favor revisa los logs del servidor para más detalles. El servidor está devolviendo HTML (probablemente una página de error) en lugar de JSON.';
            } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
                errorMessage = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.';
            } else {
                errorMessage = error.message;
            }
            
            Swal.fire({
                title: 'Error',
                text: errorMessage,
                icon: 'error',
                confirmButtonColor: '#EF4444',
                footer: 'Revisa la consola del navegador (F12) para más detalles'
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