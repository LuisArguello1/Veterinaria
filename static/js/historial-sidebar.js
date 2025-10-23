/**
 * Módulo para manejar la navegación al Historial Médico desde el sidebar
 * Este script maneja la selección de mascota antes de ir al historial
 */

document.addEventListener('DOMContentLoaded', function() {
    const historialLink = document.getElementById('historial-medico-link');
    
    if (!historialLink) return;
    
    // Interceptar el clic en el enlace de Historial Médico
    historialLink.addEventListener('click', async function(e) {
        e.preventDefault();
        
        try {
            // Obtener las mascotas del usuario
            const response = await fetch('/mascota/get-user-pets/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });
            
            if (!response.ok) {
                throw new Error('Error al cargar las mascotas');
            }
            
            const data = await response.json();
            
            if (!data.mascotas || data.mascotas.length === 0) {
                showNotification('No tienes mascotas registradas', 'warning');
                setTimeout(() => {
                    window.location.href = '/mascota/';
                }, 2000);
                return;
            }
            
            // Si solo tiene una mascota, ir directamente
            if (data.mascotas.length === 1) {
                window.location.href = `/mascota/${data.mascotas[0].id}/historial/`;
                return;
            }
            
            // Si tiene múltiples mascotas, mostrar selector
            mostrarSelectorMascotas(data.mascotas);
            
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al cargar las mascotas', 'error');
        }
    });
});

/**
 * Muestra un modal para seleccionar la mascota
 */
function mostrarSelectorMascotas(mascotas) {
    // Crear modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
    modal.id = 'modal-selector-mascota';
    
    modal.innerHTML = `
        <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div class="bg-gradient-to-r from-green-600 to-green-800 p-6 text-white">
                <h2 class="text-2xl font-bold flex items-center gap-2">
                    <i class="fas fa-file-medical-alt"></i>
                    Selecciona una Mascota
                </h2>
                <p class="text-white/90 mt-1">Elige la mascota para ver su historial médico</p>
            </div>
            
            <div class="p-6 overflow-y-auto max-h-96">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${mascotas.map(mascota => `
                        <div class="mascota-card cursor-pointer border-2 border-gray-200 rounded-lg p-4 hover:border-green-500 hover:shadow-lg transition-all duration-200"
                             data-mascota-id="${mascota.id}">
                            <div class="flex items-center gap-3">
                                <div class="w-16 h-16 rounded-full overflow-hidden bg-gray-200 flex-shrink-0">
                                    ${mascota.foto ? 
                                        `<img src="${mascota.foto}" alt="${mascota.nombre}" class="w-full h-full object-cover">` :
                                        `<div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-green-400 to-green-600">
                                            <i class="fas fa-dog text-white text-2xl"></i>
                                        </div>`
                                    }
                                </div>
                                <div class="flex-1 min-w-0">
                                    <h3 class="font-bold text-lg text-gray-900 truncate">${mascota.nombre}</h3>
                                    <p class="text-sm text-gray-600">${mascota.raza || 'Raza no especificada'}</p>
                                    <p class="text-xs text-gray-500 mt-1">
                                        <i class="fas fa-venus-mars"></i> ${mascota.sexo || 'N/A'}
                                    </p>
                                </div>
                                <i class="fas fa-chevron-right text-green-600"></i>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="border-t border-gray-200 p-4 flex justify-end">
                <button id="cerrar-modal" class="px-6 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg font-medium transition-colors">
                    Cancelar
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Agregar eventos de clic a las tarjetas
    modal.querySelectorAll('.mascota-card').forEach(card => {
        card.addEventListener('click', function() {
            const mascotaId = this.dataset.mascotaId;
            window.location.href = `/mascota/${mascotaId}/historial/`;
        });
    });
    
    // Cerrar modal
    modal.querySelector('#cerrar-modal').addEventListener('click', () => {
        modal.remove();
    });
    
    // Cerrar al hacer clic fuera
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Muestra una notificación temporal
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white font-medium animate-slide-in-right ${
        type === 'error' ? 'bg-red-500' : 
        type === 'warning' ? 'bg-yellow-500' : 
        type === 'success' ? 'bg-green-500' : 
        'bg-blue-500'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
