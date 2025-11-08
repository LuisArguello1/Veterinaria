/**
 * Módulo de Mapa Interactivo de Mascotas Perdidas y Encontradas
 * Utiliza Mapbox GL JS para visualizar mascotas en un mapa de Ecuador
 */

// Variables globales
let map = null;
let markers = [];
let mascotasData = [];
let filtroActual = 'todas';

/**
 * Inicializa el mapa cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🗺️ Iniciando módulo de mapa de mascotas...');
    
    // Verificar que tenemos el token de Mapbox
    if (!window.MAPBOX_CONFIG || !window.MAPBOX_CONFIG.token) {
        console.error('❌ Token de Mapbox no configurado');
        mostrarError('No se pudo cargar el mapa: Token de Mapbox no configurado');
        mostrarLoading(false);
        return;
    }

    console.log('✅ Token de Mapbox detectado');
    console.log('📍 Centro del mapa:', window.MAPBOX_CONFIG.centerEcuador);

    // Inicializar Mapbox
    mapboxgl.accessToken = window.MAPBOX_CONFIG.token;

    // Crear el mapa
    inicializarMapa();

    // Configurar event listeners para filtros
    configurarFiltros();

    // Cargar datos de mascotas
    cargarMascotas();
});

/**
 * Inicializa el mapa de Mapbox centrado en Ecuador
 * Usando formato Mapbox GL JS v3.x según documentación oficial
 */
function inicializarMapa() {
    try {
        console.log('🗺️ Creando instancia del mapa...');

        // Crear el mapa usando el formato v3.x con config.basemap
        map = new mapboxgl.Map({
            container: 'mapa',
            center: window.MAPBOX_CONFIG.centerEcuador,
            zoom: window.MAPBOX_CONFIG.zoom,
            maxBounds: [
                [-92.0, -6.0], // Suroeste de Ecuador
                [-75.0, 2.0]   // Noreste de Ecuador
            ],
            // Configuración moderna v3.x con basemap theme
            config: {
                basemap: { 
                    theme: 'standard', // Opciones: 'standard', 'faded', 'monochrome'
                    lightPreset: 'day' // Opciones: 'day', 'night', 'dusk', 'dawn'
                }
            },
            projection: 'mercator',
            attributionControl: true
        });

        // Manejar errores de carga del mapa
        map.on('error', function(e) {
            console.error('⚠️ Error en el mapa:', e.error);
            
            // Si es un error 403/401, mostrar mensaje específico
            if (e.error && (e.error.status === 403 || e.error.status === 401)) {
                console.error('❌ Error de autenticación con Mapbox API');
                console.error('💡 Verifica tu token en: https://account.mapbox.com/access-tokens/');
                console.error('💡 Asegúrate de que el token tenga los permisos necesarios');
                
                // Intentar con tema alternativo
                try {
                    console.warn('🔄 Intentando con tema "faded"...');
                    map.setConfig({
                        basemap: { theme: 'faded' }
                    });
                } catch (err) {
                    console.error('Error cambiando tema:', err);
                }
            }
        });

        // Agregar controles de navegación
        map.addControl(new mapboxgl.NavigationControl(), 'top-right');

        // Agregar control de geolocalización
        const geolocateControl = new mapboxgl.GeolocateControl({
            positionOptions: {
                enableHighAccuracy: true
            },
            trackUserLocation: true,
            showUserHeading: true
        });
        map.addControl(geolocateControl, 'top-right');

        // Agregar control de pantalla completa
        map.addControl(new mapboxgl.FullscreenControl(), 'top-right');

        // Agregar control de escala
        map.addControl(new mapboxgl.ScaleControl({
            maxWidth: 100,
            unit: 'metric'
        }), 'bottom-left');

        // Evento cuando el mapa está completamente cargado
        map.on('load', function() {
            console.log('✅ Mapa cargado exitosamente');
            const center = map.getCenter();
            console.log('📊 Centro:', `[${center.lng.toFixed(4)}, ${center.lat.toFixed(4)}]`);
            console.log('🔍 Zoom:', map.getZoom().toFixed(2));
            console.log('🔑 Token configurado:', window.MAPBOX_CONFIG.token ? 'Sí' : 'No');
            console.log('🎨 Tema del mapa: standard');
        });

        // Evento cuando hay un cambio de estilo
        map.on('styledata', function() {
            console.log('🎨 Datos de estilo cargados');
        });

    } catch (error) {
        console.error('❌ Error fatal inicializando el mapa:', error);
        console.error('Stack trace:', error.stack);
        mostrarError('Error al inicializar el mapa: ' + error.message);
        mostrarLoading(false);
    }
}

/**
 * Configura los event listeners para los botones de filtro
 */
function configurarFiltros() {
    const botonesFiltro = document.querySelectorAll('.filter-btn');

    botonesFiltro.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remover clase active de todos los botones
            botonesFiltro.forEach(b => b.classList.remove('active'));

            // Agregar clase active al botón clickeado
            this.classList.add('active');

            // Obtener el filtro seleccionado
            filtroActual = this.dataset.filtro;

            // Aplicar filtro
            aplicarFiltro();
        });
    });
}

/**
 * Carga las mascotas desde la API
 */
async function cargarMascotas() {
    mostrarLoading(true);

    try {
        const response = await fetch(window.MAPBOX_CONFIG.apiEndpoint);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            mascotasData = data.mascotas;
            console.log('🗺️ DATOS RECIBIDOS DEL SERVIDOR:');
            console.log(`   Total mascotas: ${data.count}`);
            console.log('   Desglose por tipo:');
            
            // Contar por tipo
            const perdidas = mascotasData.filter(m => m.tipo === 'perdida').length;
            const reportes = mascotasData.filter(m => m.tipo === 'reporte_encontrada').length;
            
            console.log(`   - Perdidas: ${perdidas}`);
            console.log(`   - Reportes encontrada: ${reportes}`);
            
            // Mostrar detalles de cada mascota
            mascotasData.forEach((m, index) => {
                console.log(`   ${index + 1}. ${m.nombre} - Tipo: ${m.tipo}, Estado: ${m.estado}, Tiene foto: ${m.foto ? 'Sí' : 'No'}`);
            });

            // Actualizar estadísticas
            actualizarEstadisticas();

            // Mostrar reportes en cards (solo los del usuario)
            mostrarReportesCards();

            // Mostrar marcadores en el mapa
            mostrarMarcadores();
        } else {
            throw new Error(data.error || 'Error desconocido');
        }

    } catch (error) {
        console.error('Error cargando mascotas:', error);
        mostrarError('Error al cargar las mascotas. Por favor, intenta nuevamente.');
    } finally {
        mostrarLoading(false);
    }
}

/**
 * Actualiza las estadísticas en el panel
 */
function actualizarEstadisticas() {
    const total = mascotasData.length;
    const perdidas = mascotasData.filter(m => m.tipo === 'perdida' || m.estado === 'perdida').length;
    const reportes = mascotasData.filter(m => m.tipo === 'reporte_encontrada' || m.estado === 'reporte_encontrada').length;

    document.getElementById('total-mascotas').textContent = total;
    document.getElementById('total-perdidas').textContent = perdidas;
    document.getElementById('total-encontradas').textContent = reportes;
}

/**
 * Muestra los marcadores en el mapa
 */
function mostrarMarcadores() {
    // Limpiar marcadores existentes
    limpiarMarcadores();

    // Filtrar mascotas según el filtro actual
    const mascotasFiltradas = filtrarMascotas();

    // Crear un marcador para cada mascota
    mascotasFiltradas.forEach(mascota => {
        crearMarcador(mascota);
    });

    // Ajustar el zoom para mostrar todos los marcadores
    if (mascotasFiltradas.length > 0) {
        ajustarZoomAMarcadores(mascotasFiltradas);
    }
}

/**
 * Filtra las mascotas según el filtro actual
 */
function filtrarMascotas() {
    if (filtroActual === 'todas') {
        return mascotasData;
    } else if (filtroActual === 'perdidas') {
        return mascotasData.filter(m => m.tipo === 'perdida' || m.estado === 'perdida');
    } else if (filtroActual === 'encontradas' || filtroActual === 'reportes') {
        return mascotasData.filter(m => m.tipo === 'reporte_encontrada' || m.estado === 'reporte_encontrada' || m.estado === 'encontrada');
    }
    return mascotasData;
}

/**
 * Crea un marcador personalizado para una mascota o reporte
 */
function crearMarcador(mascota) {
    // Validar coordenadas
    if (!mascota.longitud || !mascota.latitud) {
        console.warn(`⚠️ Mascota ${mascota.nombre} no tiene coordenadas válidas`);
        return;
    }
    
    // Crear elemento HTML para el marcador
    const el = document.createElement('div');
    
    // Determinar el tipo de marcador (reporte_encontrada o perdida)
    const esReporte = mascota.tipo === 'reporte_encontrada' || mascota.estado === 'reporte_encontrada';
    const claseEstado = esReporte ? 'encontrada' : 'perdida';
    
    console.log(`🗺️ Creando marcador: ${mascota.nombre} | Tipo: ${mascota.tipo} | Estado: ${mascota.estado} | Es reporte: ${esReporte} | Clase: ${claseEstado}`);
    console.log(`   Coordenadas: [${mascota.longitud}, ${mascota.latitud}]`);
    
    el.className = `custom-marker ${claseEstado}`;
    el.innerHTML = `<i class="fas fa-paw"></i>`;
    
    // Crear popup ANTES de crear el marcador
    const popup = crearPopup(mascota);

    // Crear el marcador con el popup ya configurado
    const marker = new mapboxgl.Marker({
        element: el,
        anchor: 'bottom'
    })
        .setLngLat([mascota.longitud, mascota.latitud])
        .setPopup(popup)
        .addTo(map);

    // Hacer el marcador clickeable
    el.style.cursor = 'pointer';
    
    // Agregar evento click directo al elemento
    el.addEventListener('click', (e) => {
        e.stopPropagation();
        // Cerrar otros popups abiertos
        markers.forEach(m => {
            if (m !== marker && m.getPopup().isOpen()) {
                m.togglePopup();
            }
        });
        // Abrir este popup
        marker.togglePopup();
    });

    // Guardar referencia al marcador
    markers.push(marker);
    
    console.log(`   ✅ Marcador creado y agregado al mapa (Total marcadores: ${markers.length})`);
}

/**
 * Crea el contenido HTML del popup para una mascota o reporte
 */
function crearPopup(mascota) {
    // Usar fecha_reporte para reportes o fecha_ubicacion para perdidas
    const fecha = mascota.fecha_reporte || mascota.fecha_ubicacion;
    const fechaFormateada = fecha
        ? new Date(fecha).toLocaleDateString('es-EC', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
        : 'No especificada';

    // La API envía 'foto' no 'foto_url'
    const imagenHTML = mascota.foto 
        ? `<img src="${mascota.foto}" alt="${mascota.nombre}" class="popup-image" onerror="this.src='/static/img/default-dog.jpg'">`
        : `<div class="popup-image" style="display: flex; align-items: center; justify-content: center; background: #f0f0f0;">
               <i class="fas fa-dog" style="font-size: 3rem; color: #ccc;"></i>
           </div>`;

    // Determinar tipo: reporte_encontrada o perdida
    const esReporte = mascota.tipo === 'reporte_encontrada' || mascota.estado === 'reporte_encontrada';
    const estadoTexto = esReporte ? '¡Reportada como Encontrada!' : 'Perdida';
    const estadoIcono = esReporte ? 'check-circle' : 'exclamation-circle';
    const estadoClase = esReporte ? 'encontrada' : 'perdida';

    const popupHTML = `
        <div class="popup-content">
            ${imagenHTML}
            <div class="popup-body">
                <div class="popup-header">
                    <h3 class="popup-name">${mascota.nombre}</h3>
                    <span class="popup-estado ${estadoClase}">
                        <i class="fas fa-${estadoIcono}"></i>
                        ${estadoTexto}
                    </span>
                </div>

                ${esReporte ? `
                    <div class="popup-info" style="background: #d1fae5; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem; font-size: 0.85rem;">
                        <div class="popup-info-item" style="margin: 0;">
                            <i class="fas fa-user" style="color: #059669;"></i>
                            <div>
                                <strong>Reportado por:</strong> ${mascota.reportante || 'Anónimo'}
                                ${mascota.reportante_telefono ? `<br><small><i class="fas fa-phone"></i> ${mascota.reportante_telefono}</small>` : ''}
                            </div>
                        </div>
                    </div>
                ` : ''}

                <div class="popup-info">
                    <div class="popup-info-item">
                        <i class="fas fa-paw"></i>
                        <div><strong>Raza:</strong> ${mascota.raza || 'No especificada'}</div>
                    </div>
                </div>

                <div class="popup-ubicacion">
                    <i class="fas fa-map-marker-alt"></i>
                    <strong>${esReporte ? 'Encontrada:' : 'Perdida:'}</strong> ${mascota.ubicacion_descripcion}
                    <br>
                    <small style="color: #666; margin-left: 1.2rem;">
                        <i class="fas fa-clock"></i> ${fechaFormateada}
                    </small>
                </div>

                ${!esReporte ? `
                    <div class="popup-actions">
                        <button onclick="window.location.href='/scanner/'" class="popup-btn popup-btn-primary" style="width: 100%;">
                            <i class="fas fa-qrcode"></i>
                            ¡La encontré!
                        </button>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    return new mapboxgl.Popup({
        maxWidth: '280px',
        closeButton: true,
        closeOnClick: false
    }).setHTML(popupHTML);
}

/**
 * Limpia todos los marcadores del mapa
 */
function limpiarMarcadores() {
    markers.forEach(marker => marker.remove());
    markers = [];
}

/**
 * Aplica el filtro actual y actualiza los marcadores
 */
function aplicarFiltro() {
    mostrarMarcadores();
}

/**
 * Ajusta el zoom del mapa para mostrar todos los marcadores
 */
function ajustarZoomAMarcadores(mascotas) {
    if (mascotas.length === 0) return;

    const bounds = new mapboxgl.LngLatBounds();

    mascotas.forEach(mascota => {
        bounds.extend([mascota.longitud, mascota.latitud]);
    });

    map.fitBounds(bounds, {
        padding: { top: 50, bottom: 50, left: 50, right: 50 },
        maxZoom: 12
    });
}

/**
 * Muestra u oculta el overlay de carga
 */
function mostrarLoading(mostrar) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        if (mostrar) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: mensaje,
        confirmButtonColor: '#dc3545'
    });
}

/**
 * Muestra los reportes de mascotas encontradas en cards
 */
function mostrarReportesCards() {
    const reportesContainer = document.getElementById('reportes-container');
    const reportesList = document.getElementById('reportes-list');
    
    // Filtrar solo los reportes de encontrada
    const reportes = mascotasData.filter(m => m.tipo === 'reporte_encontrada');
    
    console.log('📋 Mostrando reportes en cards:', reportes.length);
    
    if (reportes.length === 0) {
        reportesContainer.style.display = 'none';
        return;
    }
    
    // Mostrar el contenedor
    reportesContainer.style.display = 'block';
    
    // Limpiar lista
    reportesList.innerHTML = '';
    
    // Crear card para cada reporte
    reportes.forEach(reporte => {
        const card = crearReporteCard(reporte);
        reportesList.appendChild(card);
    });
}

/**
 * Crea una card HTML para un reporte
 */
function crearReporteCard(reporte) {
    const card = document.createElement('div');
    card.className = 'reporte-card';
    
    const fechaFormateada = reporte.fecha_reporte 
        ? new Date(reporte.fecha_reporte).toLocaleDateString('es-EC', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
        : 'Fecha no especificada';
    
    card.innerHTML = `
        <div class="reporte-card-header">
            <h3 class="reporte-card-title">
                <i class="fas fa-dog"></i>
                ${reporte.nombre}
            </h3>
            <span class="reporte-card-badge">
                <i class="fas fa-check-circle"></i> Encontrada
            </span>
        </div>
        
        <div class="reporte-card-body">
            <div class="reporte-foto-container">
                ${reporte.foto ? 
                    `<img src="${reporte.foto}" alt="${reporte.nombre}" class="reporte-foto" onerror="this.parentElement.innerHTML='<i class=\\'fas fa-dog reporte-foto-placeholder\\'></i>'">` :
                    `<i class="fas fa-dog reporte-foto-placeholder"></i>`
                }
            </div>
            
            <div class="reporte-info">
                <div class="reporte-info-item">
                    <i class="fas fa-user"></i>
                    <div class="reporte-info-content">
                        <div class="reporte-info-label">Reportado por</div>
                        <div class="reporte-info-value">${reporte.reportante || 'Anónimo'}</div>
                        ${reporte.reportante_telefono ? `<div class="reporte-info-value"><i class="fas fa-phone"></i> ${reporte.reportante_telefono}</div>` : ''}
                        ${reporte.reportante_email ? `<div class="reporte-info-value"><i class="fas fa-envelope"></i> ${reporte.reportante_email}</div>` : ''}
                    </div>
                </div>
                
                <div class="reporte-info-item">
                    <i class="fas fa-map-marker-alt"></i>
                    <div class="reporte-info-content">
                        <div class="reporte-info-label">Ubicación</div>
                        <div class="reporte-info-value">${reporte.ubicacion_descripcion || 'No especificada'}</div>
                    </div>
                </div>
                
                <div class="reporte-info-item">
                    <i class="fas fa-clock"></i>
                    <div class="reporte-info-content">
                        <div class="reporte-info-label">Fecha del reporte</div>
                        <div class="reporte-info-value">${fechaFormateada}</div>
                    </div>
                </div>
                
                ${reporte.caracteristicas ? `
                <div class="reporte-info-item">
                    <i class="fas fa-info-circle"></i>
                    <div class="reporte-info-content">
                        <div class="reporte-info-label">Características</div>
                        <div class="reporte-info-value">${reporte.caracteristicas}</div>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
        
        <div class="reporte-card-actions">
            <button onclick="confirmarReporte(${reporte.reporte_id})" class="reporte-btn reporte-btn-confirm">
                <i class="fas fa-check"></i>
                Sí es mi mascota
            </button>
            <button onclick="descartarReporte(${reporte.reporte_id})" class="reporte-btn reporte-btn-dismiss">
                <i class="fas fa-times"></i>
                No es mi mascota
            </button>
            <button onclick="verEnMapa(${reporte.latitud}, ${reporte.longitud})" class="reporte-btn reporte-btn-view">
                <i class="fas fa-map"></i>
                Ver en mapa
            </button>
        </div>
    `;
    
    return card;
}

/**
 * Centra el mapa en una ubicación específica
 */
function verEnMapa(lat, lng) {
    if (map) {
        map.flyTo({
            center: [lng, lat],
            zoom: 15,
            duration: 2000
        });
        
        // Scroll al mapa
        document.getElementById('mapa').scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Descarta un reporte de mascota encontrada
 */
async function descartarReporte(reporteId) {
    const result = await Swal.fire({
        title: '¿Descartar este reporte?',
        text: 'Esta mascota no es tuya. El reporte será eliminado.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, descartar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#6b7280'
    });

    if (result.isConfirmed) {
        try {
            const response = await fetch(`/api/reporte/${reporteId}/descartar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    icon: 'info',
                    title: 'Reporte descartado',
                    text: data.message,
                    confirmButtonColor: '#3b82f6'
                });
                
                // Recargar datos
                await cargarMascotas();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Error al descartar reporte:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Hubo un problema al descartar el reporte.'
            });
        }
    }
}

/**
 * Obtiene el valor de una cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Confirma un reporte de mascota encontrada
 */
async function confirmarReporte(reporteId) {
    const result = await Swal.fire({
        title: '¿Confirmar que es tu mascota?',
        text: 'Al confirmar, se marcará tu mascota como encontrada y se eliminará del mapa de búsqueda.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, es mi mascota',
        cancelButtonText: 'No, no es',
        confirmButtonColor: '#059669',
        cancelButtonColor: '#dc2626'
    });

    if (result.isConfirmed) {
        try {
            const response = await fetch(`/api/reporte/${reporteId}/confirmar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Excelente!',
                    text: data.message,
                    confirmButtonColor: '#059669'
                });
                
                // Recargar datos del mapa
                await cargarMascotas();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Error al confirmar reporte:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Hubo un problema al confirmar el reporte. Por favor, intenta de nuevo.'
            });
        }
    }
}
