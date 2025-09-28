/**
 * Manejo de pestañas de mascotas
 * Gestiona la navegación entre diferentes mascotas en la vista de detalle
 */

// Configuración global para las pestañas de mascotas
window.mascotaTabs = {
    initialized: false,
    activeTab: null
};

/**
 * Inicializa el sistema de pestañas de mascotas
 */
function initializeMascotaTabs() {
    // Evitar múltiples inicializaciones
    if (window.mascotaTabs.initialized) {
        return;
    }

    const mascotaBtns = document.querySelectorAll('.mascota-tab-btn');
    const mascotaDetails = document.querySelectorAll('.mascota-detail');
    
    // Solo inicializar si hay múltiples mascotas
    if (mascotaBtns.length === 0) {
        console.log('No hay pestañas de mascotas para inicializar');
        return;
    }

    console.log(`Inicializando sistema de pestañas para ${mascotaBtns.length} mascotas`);

    // Marcar como inicializado
    window.mascotaTabs.initialized = true;
    
    // Configurar event listeners para cada botón
    mascotaBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            switchMascotaTab(target, mascotaBtns, mascotaDetails);
        });
    });
    
    // Activar la primera pestaña por defecto
    if (mascotaBtns.length > 0) {
        activateFirstMascotaTab(mascotaBtns);
    }
}

/**
 * Cambia entre pestañas de mascotas
 * @param {string} target - ID del elemento objetivo
 * @param {NodeList} mascotaBtns - Lista de botones de pestañas
 * @param {NodeList} mascotaDetails - Lista de contenedores de detalles
 */
function switchMascotaTab(target, mascotaBtns, mascotaDetails) {
    // Desactivar todos los botones y ocultar todos los detalles
    mascotaBtns.forEach(btn => {
        btn.classList.remove('active', 'bg-primary-700', 'text-white');
        btn.classList.add('bg-white', 'text-gray-700', 'hover:bg-gray-100');
    });
    
    // Ocultar todos los detalles de mascotas
    mascotaDetails.forEach(detail => {
        detail.classList.add('hidden');
    });
    
    // Activar el botón seleccionado
    const activeBtn = document.querySelector(`[data-target="${target}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-primary-700', 'text-white');
        activeBtn.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-100');
    }
    
    // Guardar la pestaña activa
    window.mascotaTabs.activeTab = target;
    
    // Mostrar el contenido correspondiente
    const targetElement = document.getElementById(target);
    if (targetElement) {
        targetElement.classList.remove('hidden');
        console.log(`Pestaña de mascota activada: ${target}`);
    } else {
        console.warn(`Elemento objetivo no encontrado: ${target}`);
    }
}

/**
 * Activa la primera pestaña de mascota por defecto
 * @param {NodeList} mascotaBtns - Lista de botones de pestañas
 */
function activateFirstMascotaTab(mascotaBtns) {
    if (mascotaBtns.length > 0) {
        mascotaBtns[0].click();
        console.log('Primera pestaña de mascota activada automáticamente');
    }
}

/**
 * Obtiene la pestaña de mascota actualmente activa
 * @returns {string|null} - ID de la pestaña activa o null
 */
function getActiveMascotaTab() {
    return window.mascotaTabs.activeTab;
}

/**
 * Cambia a una pestaña específica de mascota por ID
 * @param {string|number} mascotaId - ID de la mascota
 */
function switchToMascotaTab(mascotaId) {
    const target = `mascota-${mascotaId}`;
    const btn = document.querySelector(`[data-target="${target}"]`);
    if (btn) {
        btn.click();
    } else {
        console.warn(`Pestaña de mascota no encontrada: ${target}`);
    }
}

// Inicialización automática cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Pequeño delay para asegurar que todos los elementos estén renderizados
    setTimeout(initializeMascotaTabs, 100);
});

// Exportar funciones para uso externo
window.mascotaTabsUtils = {
    initialize: initializeMascotaTabs,
    switchTo: switchToMascotaTab,
    getActive: getActiveMascotaTab
};