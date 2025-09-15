// Archivo para manejar la visualización dinámica de campos en el formulario de usuarios

/**
 * Muestra u oculta los campos específicos de veterinario según el rol seleccionado
 */
document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('id_role');
    const vetFieldsContainer = document.getElementById('vet-fields-container');
    
    // Si no existen estos elementos, no hacemos nada
    if (!roleSelect || !vetFieldsContainer) return;
    
    // Función para mostrar u ocultar campos según el rol
    function toggleVetFields() {
        const selectedRole = roleSelect.value;
        
        // Si el rol es VET (veterinario), mostramos los campos específicos
        if (selectedRole === 'VET') {
            vetFieldsContainer.classList.remove('hidden');
            
            // Hacer los campos requeridos
            const specializationInput = document.getElementById('id_specialization');
            const licenseInput = document.getElementById('id_license_number');
            
            if (specializationInput) specializationInput.setAttribute('required', 'required');
            if (licenseInput) licenseInput.setAttribute('required', 'required');
        } else {
            vetFieldsContainer.classList.add('hidden');
            
            // Quitar la validación requerida
            const specializationInput = document.getElementById('id_specialization');
            const licenseInput = document.getElementById('id_license_number');
            
            if (specializationInput) specializationInput.removeAttribute('required');
            if (licenseInput) licenseInput.removeAttribute('required');
        }
    }
    
    // Ejecutar al cargar para establecer el estado inicial
    toggleVetFields();
    
    // Añadir evento para cuando cambie el selector de rol
    roleSelect.addEventListener('change', toggleVetFields);
});
