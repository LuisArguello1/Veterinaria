/**
 * Configuración inicial de la aplicación
 * Maneja la configuración global y inicialización de componentes
 */

// Configuración global de la aplicación
window.appConfig = {
    activeBiometriaId: null,
    initialized: false
};

/**
 * Inicializa la configuración de la aplicación
 * @param {Object} config - Objeto de configuración del servidor
 */
function initializeAppConfig(config = {}) {
    // Merge configuración del servidor con la configuración por defecto
    window.appConfig = {
        ...window.appConfig,
        ...config,
        initialized: true
    };
    
    console.log('Configuración de la aplicación inicializada:', window.appConfig);
}

/**
 * Obtiene un valor de configuración
 * @param {string} key - Clave de configuración
 * @param {*} defaultValue - Valor por defecto si no existe
 * @returns {*} Valor de configuración
 */
function getConfig(key, defaultValue = null) {
    return window.appConfig[key] || defaultValue;
}

/**
 * Establece un valor de configuración
 * @param {string} key - Clave de configuración
 * @param {*} value - Valor a establecer
 */
function setConfig(key, value) {
    window.appConfig[key] = value;
}

// Exportar utilidades de configuración
window.configUtils = {
    init: initializeAppConfig,
    get: getConfig,
    set: setConfig
};