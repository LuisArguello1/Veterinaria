// Archivo para manejar la visualización dinámica de campos en el formulario de usuarios

/**
 * Muestra u oculta los campos específicos de veterinario según el rol seleccionado
 */
document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('id_role');
    const vetSectionHeader = document.getElementById('vet-section-header');
    const vetSpecializationField = document.getElementById('vet-specialization-field');
    const vetLicenseField = document.getElementById('vet-license-field');
    
    // Función para mostrar u ocultar campos según el rol
    function toggleVetFields() {
        if (!roleSelect) return;
        
        const selectedRole = roleSelect.value;
        
        // Si el rol es VET (veterinario), mostramos los campos específicos
        if (selectedRole === 'VET') {
            if (vetSectionHeader) vetSectionHeader.classList.remove('hidden');
            if (vetSpecializationField) vetSpecializationField.classList.remove('hidden');
            if (vetLicenseField) vetLicenseField.classList.remove('hidden');
            
            // Hacer los campos requeridos
            const specializationInput = document.getElementById('id_specialization');
            const licenseInput = document.getElementById('id_license_number');
            
            if (specializationInput) specializationInput.setAttribute('required', 'required');
            if (licenseInput) licenseInput.setAttribute('required', 'required');
        } else {
            if (vetSectionHeader) vetSectionHeader.classList.add('hidden');
            if (vetSpecializationField) vetSpecializationField.classList.add('hidden');
            if (vetLicenseField) vetLicenseField.classList.add('hidden');
            
            // Quitar la validación requerida
            const specializationInput = document.getElementById('id_specialization');
            const licenseInput = document.getElementById('id_license_number');
            
            if (specializationInput) specializationInput.removeAttribute('required');
            if (licenseInput) licenseInput.removeAttribute('required');
        }
    }
    
    // Ejecutar al cargar para establecer el estado inicial
    if (roleSelect) {
        toggleVetFields();
        // Añadir evento para cuando cambie el selector de rol
        roleSelect.addEventListener('change', toggleVetFields);
    }
    
    // Validación de imagen de perfil
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validar tamaño (5MB máximo)
                if (file.size > 5 * 1024 * 1024) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Imagen muy grande',
                        text: 'La imagen no debe superar los 5MB. Por favor, selecciona una imagen más pequeña.',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#d33'
                    });
                    e.target.value = ''; // Limpiar el input
                    return;
                }
                
                // Validar tipo de archivo
                const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg'];
                if (!validImageTypes.includes(file.type)) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Tipo de archivo inválido',
                        text: 'Por favor, selecciona un archivo de imagen válido (JPG, PNG, GIF, WEBP).',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#d33'
                    });
                    e.target.value = ''; // Limpiar el input
                    return;
                }

                // Mostrar preview de la imagen si existe un contenedor de preview
                const reader = new FileReader();
                reader.onload = function(event) {
                    const previewImg = document.querySelector('.flex-shrink-0 img');
                    if (previewImg) {
                        previewImg.src = event.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
