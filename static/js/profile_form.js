// Validación de imagen de perfil
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('id_image');
    const imagePreview = document.querySelector('img[alt*="' + (document.querySelector('.w-28') ? '' : '') + '"]');
    
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

                // Mostrar preview de la nueva imagen
                const reader = new FileReader();
                reader.onload = function(event) {
                    // Buscar la imagen de preview en el DOM
                    const previewImg = document.querySelector('.w-28.h-28 img');
                    if (previewImg) {
                        previewImg.src = event.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});